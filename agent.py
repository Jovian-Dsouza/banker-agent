from datetime import datetime, timezone
from uuid import uuid4
from typing import Any, Dict, List, Optional
import json
import os
import re
from dotenv import load_dotenv
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

load_dotenv()

agent = Agent(name="Banker agent", port=8008, mailbox=True, publish_agent_details=True)

class GameState(Model):
    round: int
    remaining_cards: List[int]
    burnt_cards: List[int]
    user_card: Optional[int] = None

class BankerOffer(Model):
    offer: int
    expected_value: int
    house_edge: float
    round: int
    sentiment: str
    message: str
    psychology: str

def create_text_chat(text: str, end_session: bool = False) -> ChatMessage:
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent(type="end-session"))
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=content,
    )

def get_default_game_state() -> Dict[str, Any]:
    """Get default game state for testing."""
    return {
        "round": 1,
        "remaining_cards": [1, 5, 10, 25, 50, 100, 500, 1000, 2500, 5000, 10000, 25000, 50000, 75000, 100000, 200000, 300000, 400000, 500000, 750000, 1000000],
        "burnt_cards": [],
        "user_card": None
    }

def parse_game_state_from_message(message: str) -> Dict[str, Any]:
    """Parse game state from user message."""
    # Try to extract from message first
    extracted_state = extract_game_state_from_message(message)
    if extracted_state:
        return extracted_state
    
    # Default game state
    return get_default_game_state()

metta = MeTTa()
initialize_banker_knowledge(metta)
rag = BankerRAG(metta)
llm = LLM(api_key=os.getenv("ASI_ONE_API_KEY"))

chat_proto = Protocol(spec=chat_protocol_spec)

@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    ctx.storage.set(str(ctx.session), sender)
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(timezone.utc), acknowledged_msg_id=msg.msg_id),
    )

    for item in msg.content:
        if isinstance(item, StartSessionContent):
            ctx.logger.info(f"Got a start session message from {sender}")
            # Send welcome message
            welcome_msg = """🎰 Welcome to the Banker's Table! 🎰

I'm the Banker, and I'm here to make you offers you can't refuse... or can you?

To get started, tell me about your game state. For example:
- "Round 1, remaining cards: [1, 5, 10, 25, 50, 100, 500, 1000, 2500, 5000, 10000, 25000, 50000, 75000, 100000, 200000, 300000, 400000, 500000, 750000, 1000000]"
- "I'm confident, round 2, cards left: [100, 500, 1000, 5000, 10000, 25000, 100000, 500000, 1000000]"

Or just say something like "Make me an offer" and I'll use a default game state.

Remember: The house always wins! 😈"""
            await ctx.send(sender, create_text_chat(welcome_msg))
            continue
        elif isinstance(item, TextContent):
            user_message = item.text.strip()
            ctx.logger.info(f"Got a banker query from {sender}: {user_message}")
            
            try:
                # Parse game state from message
                game_state = parse_game_state_from_message(user_message)
                
                # Process banker query
                response = process_banker_query(
                    user_message, 
                    rag, 
                    llm,
                    game_state["remaining_cards"],
                    game_state["burnt_cards"],
                    game_state["round"]
                )
                
                # Format response
                if isinstance(response, dict):
                    answer_text = f"**🎯 Round {response['game_state']['round']} Offer**\n\n"
                    answer_text += f"💰 **My Offer: ${response['offer']:,}**\n\n"
                    answer_text += f"💬 **{response['humanized_answer']}**\n\n"
                    answer_text += f"🧠 **Psychology**: {response['psychology']}\n\n"
                    answer_text += f"📊 **Game State**:\n"
                    answer_text += f"   • Expected Value: ${response['game_state']['expected_value']:,}\n"
                    answer_text += f"   • House Edge: {response['game_state']['house_edge']:.1%}\n"
                    answer_text += f"   • Remaining Cards: {len(response['game_state']['remaining_cards'])} cards\n"
                    answer_text += f"   • Player Sentiment: {response['game_state']['sentiment']}\n"
                    answer_text += f"   • Cards: {response['game_state']['remaining_cards']}"
                else:
                    answer_text = str(response)
                
                await ctx.send(sender, create_text_chat(answer_text))
                
            except Exception as e:
                ctx.logger.error(f"Error processing banker query: {e}")
                await ctx.send(
                    sender, 
                    create_text_chat("I apologize, but I encountered an error processing your request. Please try again with a clear game state description.")
                )
        else:
            ctx.logger.info(f"Got unexpected content from {sender}")

@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Got an acknowledgement from {sender} for {msg.acknowledged_msg_id}")

agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()