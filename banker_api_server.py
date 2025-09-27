from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, Any, Optional
import json
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Please install it with: pip install python-dotenv")
    load_dotenv = lambda: None
from uagents import Context, Model, Protocol, Agent
from hyperon import MeTTa

from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)

from metta.banker_rag import BankerRAG
from metta.knowledge import initialize_banker_knowledge
from metta.utils import LLM, process_banker_query, extract_game_state_from_message
from api_models import (
    StartGameRequest, StartGameResponse, ChatRequest, ChatResponse,
    GameStateRequest, DealActionRequest, DealActionResponse,
    GameHistoryResponse, HealthResponse, ErrorResponse,
    GameState, BankerResponse, ActiveGamesResponse
)

# load_dotenv() is called above in the try-except block

# Create the banker agent
banker_agent = Agent(name="Banker API Agent", port=8009, mailbox=True, publish_agent_details=True)

# Initialize MeTTa and RAG
metta = MeTTa()
initialize_banker_knowledge(metta)
rag = BankerRAG(metta)
llm = LLM(api_key=os.getenv("ASI_ONE_API_KEY"))

# In-memory storage for games (in production, use Redis/PostgreSQL)
active_games: Dict[str, Dict[str, Any]] = {}
game_messages: Dict[str, list] = {}

def get_default_game_state() -> Dict[str, Any]:
    """Get default game state for new games."""
    return {
        "round": 1,
        "remaining_cards": [1, 5, 10, 25, 50, 100, 500, 1000, 2500, 5000, 10000, 25000, 50000, 75000, 100000, 200000, 300000, 400000, 500000, 750000, 1000000],
        "burnt_cards": [],
        "selected_case": None,
        "current_offer": None,
        "expected_value": None,
        "house_edge": None,
        "status": "active"
    }

def create_game_state_response(game_id: str, game_data: Dict[str, Any]) -> GameState:
    """Create GameState response from game data."""
    return GameState(
        game_id=game_id,
        round=game_data.get("round", 1),
        remaining_cards=game_data.get("remaining_cards", []),
        burnt_cards=game_data.get("burnt_cards", []),
        selected_case=game_data.get("selected_case"),
        current_offer=game_data.get("current_offer"),
        expected_value=game_data.get("expected_value"),
        house_edge=game_data.get("house_edge"),
        status=game_data.get("status", "active")
    )

# REST API Endpoints

@banker_agent.on_rest_post("/start-game", StartGameRequest, StartGameResponse)
async def start_game(ctx: Context, req: StartGameRequest) -> StartGameResponse:
    """Start a new Deal or No Deal game"""
    try:
        # Generate new game ID
        game_id = str(uuid4())
        
        # Initialize game state
        game_state = get_default_game_state()
        active_games[game_id] = game_state
        game_messages[game_id] = []
        
        # Process initial banker query
        response = process_banker_query(
            "start game", 
            rag, 
            llm,
            game_state["remaining_cards"],
            game_state["burnt_cards"],
            game_state["round"]
        )
        
        # Create banker response
        if isinstance(response, dict) and response.get('offer') is not None:
            banker_message = f"**🎯 Round {response['game_state']['round']} Offer**\n\n💰 **My Offer: ${response['offer']:,}**\n\n💬 **{response['humanized_answer']}**"
            
            # Update game state with offer
            active_games[game_id]["current_offer"] = response['offer']
            active_games[game_id]["expected_value"] = response['game_state']['expected_value']
            active_games[game_id]["house_edge"] = response['game_state']['house_edge']
        else:
            banker_message = f"**💬 {response['humanized_answer']}**"
        
        # Store initial message
        game_messages[game_id].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sender": "banker",
            "message": banker_message,
            "message_type": "offer" if response.get('offer') else "conversation"
        })
        
        ctx.logger.info(f"Started new game: {game_id}")
        
        return StartGameResponse(
            game_id=game_id,
            game_state=create_game_state_response(game_id, active_games[game_id]),
            banker_message=banker_message
        )
        
    except Exception as e:
        ctx.logger.error(f"Error starting game: {e}")
        return StartGameResponse(
            game_id="",
            game_state=GameState(game_id="", round=0, remaining_cards=[], burnt_cards=[], status="error"),
            banker_message="",
            success=False,
            error=f"Failed to start game: {str(e)}"
        )

@banker_agent.on_rest_post("/chat", ChatRequest, ChatResponse)
async def chat_with_banker(ctx: Context, req: ChatRequest) -> ChatResponse:
    """Send a message to the banker and get response"""
    try:
        game_id = req.game_id
        
        if game_id not in active_games:
            return ChatResponse(
                banker_response=BankerResponse(
                    message="Game not found. Please start a new game.",
                    game_state=GameState(game_id="", round=0, remaining_cards=[], burnt_cards=[], status="error")
                ),
                success=False,
                error="Game not found"
            )
        
        game_data = active_games[game_id]
        
        # Store user message
        game_messages[game_id].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sender": "user",
            "message": req.message,
            "message_type": "text"
        })
        
        # Process banker query
        response = process_banker_query(
            req.message, 
            rag, 
            llm,
            game_data["remaining_cards"],
            game_data["burnt_cards"],
            game_data["round"]
        )
        
        # Check if player accepted/rejected deal
        user_message_lower = req.message.lower()
        deal_phrases = ["accept", "yes", "take it", "i'll take it", "agreed", "i accept", "deal accepted", "take the deal"]
        rejects_deal = any(phrase in user_message_lower for phrase in ["no deal", "reject", "pass", "no thanks", "decline", "not interested"])
        
        if rejects_deal:
            # Player rejected deal
            banker_message = "**❌ Deal Rejected**\n\n💬 **Your loss! Better luck next time!**\n\n🎰 **Game Over - Thanks for playing!**"
            active_games[game_id]["status"] = "completed"
            message_type = "game_over"
        elif any(phrase in user_message_lower for phrase in deal_phrases):
            # Player accepted deal
            offer_amount = game_data.get("current_offer", 0)
            banker_message = f"**🎉 DEAL ACCEPTED! 🎉**\n\n💰 **You've won: ${offer_amount:,}**\n\n💬 **Congratulations! You made the smart choice and walked away with guaranteed money!**\n\n🎰 **Game Over - Thanks for playing!**"
            active_games[game_id]["status"] = "completed"
            message_type = "deal_accepted"
        else:
            # Regular response
            if isinstance(response, dict):
                if response.get('offer') is not None:
                    banker_message = f"**🎯 Round {response['game_state']['round']} Offer**\n\n💰 **My Offer: ${response['offer']:,}**\n\n💬 **{response['humanized_answer']}**"
                    message_type = "offer"
                    
                    # Update game state with new offer
                    active_games[game_id]["current_offer"] = response['offer']
                    active_games[game_id]["expected_value"] = response['game_state']['expected_value']
                    active_games[game_id]["house_edge"] = response['game_state']['house_edge']
                    active_games[game_id]["round"] = response['game_state']['round']
                else:
                    banker_message = f"**💬 {response['humanized_answer']}**"
                    message_type = "conversation"
            else:
                banker_message = str(response)
                message_type = "conversation"
        
        # Store banker response
        game_messages[game_id].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sender": "banker",
            "message": banker_message,
            "message_type": message_type
        })
        
        # Create banker response object
        banker_response = BankerResponse(
            message=banker_message,
            offer=active_games[game_id].get("current_offer"),
            game_state=create_game_state_response(game_id, active_games[game_id]),
            message_type=message_type,
            sentiment=response.get('game_state', {}).get('sentiment') if isinstance(response, dict) else None
        )
        
        ctx.logger.info(f"Processed chat for game {game_id}: {req.message[:50]}...")
        
        return ChatResponse(banker_response=banker_response)
        
    except Exception as e:
        ctx.logger.error(f"Error processing chat: {e}")
        return ChatResponse(
            banker_response=BankerResponse(
                message="I apologize, but I encountered an error processing your request.",
                game_state=GameState(game_id=req.game_id or "", round=0, remaining_cards=[], burnt_cards=[], status="error")
            ),
            success=False,
            error=f"Failed to process message: {str(e)}"
        )

@banker_agent.on_rest_post("/update-game-state", GameStateRequest, ChatResponse)
async def update_game_state(ctx: Context, req: GameStateRequest) -> ChatResponse:
    """Update game state (remaining cards, round, etc.)"""
    try:
        if req.game_id not in active_games:
            return ChatResponse(
                banker_response=BankerResponse(
                    message="Game not found.",
                    game_state=GameState(game_id="", round=0, remaining_cards=[], burnt_cards=[], status="error")
                ),
                success=False,
                error="Game not found"
            )
        
        # Update game state
        active_games[req.game_id].update({
            "remaining_cards": req.remaining_cards,
            "burnt_cards": req.burnt_cards,
            "round": req.round,
            "selected_case": req.selected_case
        })
        
        # Process banker response with updated state
        response = process_banker_query(
            f"Game state updated: round {req.round}, remaining cards: {req.remaining_cards}", 
            rag, 
            llm,
            req.remaining_cards,
            req.burnt_cards,
            req.round
        )
        
        # Create response
        if isinstance(response, dict) and response.get('offer') is not None:
            banker_message = f"**🎯 Round {response['game_state']['round']} Offer**\n\n💰 **My Offer: ${response['offer']:,}**\n\n💬 **{response['humanized_answer']}**"
            active_games[req.game_id]["current_offer"] = response['offer']
            active_games[req.game_id]["expected_value"] = response['game_state']['expected_value']
            active_games[req.game_id]["house_edge"] = response['game_state']['house_edge']
        else:
            banker_message = f"**💬 {response['humanized_answer']}**"
        
        banker_response = BankerResponse(
            message=banker_message,
            offer=active_games[req.game_id].get("current_offer"),
            game_state=create_game_state_response(req.game_id, active_games[req.game_id]),
            message_type="offer" if response.get('offer') else "conversation"
        )
        
        return ChatResponse(banker_response=banker_response)
        
    except Exception as e:
        ctx.logger.error(f"Error updating game state: {e}")
        return ChatResponse(
            banker_response=BankerResponse(
                message="Error updating game state.",
                game_state=GameState(game_id=req.game_id, round=0, remaining_cards=[], burnt_cards=[], status="error")
            ),
            success=False,
            error=f"Failed to update game state: {str(e)}"
        )

@banker_agent.on_rest_get("/game-history/{game_id}", GameHistoryResponse)
async def get_game_history(ctx: Context, game_id: str) -> GameHistoryResponse:
    """Get chat history for a specific game"""
    try:
        if game_id not in game_messages:
            return GameHistoryResponse(
                game_id=game_id,
                messages=[],
                final_result="Game not found"
            )
        
        game_data = active_games.get(game_id, {})
        final_result = None
        total_winnings = None
        
        if game_data.get("status") == "completed":
            final_result = "completed"
            total_winnings = game_data.get("current_offer", 0)
        
        return GameHistoryResponse(
            game_id=game_id,
            messages=game_messages[game_id],
            final_result=final_result,
            total_winnings=total_winnings
        )
        
    except Exception as e:
        ctx.logger.error(f"Error getting game history: {e}")
        return GameHistoryResponse(
            game_id=game_id,
            messages=[],
            final_result="error"
        )

@banker_agent.on_rest_get("/health", HealthResponse)
async def health_check(ctx: Context) -> HealthResponse:
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        agent="banker_api_agent",
        timestamp=datetime.now(timezone.utc).isoformat()
    )

@banker_agent.on_rest_get("/active-games", ActiveGamesResponse)
async def get_active_games(ctx: Context) -> ActiveGamesResponse:
    """Get list of active games (for debugging)"""
    return ActiveGamesResponse(
        active_games=list(active_games.keys()),
        total_games=len(active_games),
        timestamp=datetime.now(timezone.utc).isoformat()
    )

if __name__ == "__main__":
    banker_agent.run()
