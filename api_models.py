from typing import List, Optional, Dict, Any
from datetime import datetime
from uagents import Model

# Base Models (define first to avoid circular dependencies)
class GameState(Model):
    """Game state information"""
    game_id: str
    round: int
    remaining_cards: List[int]
    burnt_cards: List[int]
    selected_case: Optional[int] = None
    current_offer: Optional[int] = None
    expected_value: Optional[int] = None
    house_edge: Optional[float] = None
    status: str  # "active", "completed", "abandoned"

# Request Models
class StartGameRequest(Model):
    """Request to start a new game"""
    game_id: str
    game_state: GameState

class ChatRequest(Model):
    """Request to send a message to the banker"""
    message: str
    game_id: str
    game_state: GameState
    message_history: List[Dict[str, Any]]

class GameStateRequest(Model):
    """Request to update game state"""
    game_id: str
    remaining_cards: List[int]
    burnt_cards: List[int]
    round: int
    selected_case: Optional[int] = None

class DealActionRequest(Model):
    """Request to accept or reject a deal"""
    game_id: str
    action: str  # "accept" or "reject"
    offer_amount: int

# Response Models
class BankerResponse(Model):
    """Banker's response to player"""
    message: str
    offer: Optional[int] = None
    game_state: GameState
    message_type: str = "text"  # "text", "offer", "conversation"
    sentiment: Optional[str] = None
    psychology: Optional[str] = None

class StartGameResponse(Model):
    """Response when starting a new game"""
    game_id: str
    game_state: GameState
    banker_message: str
    success: bool = True
    error: Optional[str] = None

class ChatResponse(Model):
    """Response to chat message"""
    banker_response: BankerResponse
    success: bool = True
    error: Optional[str] = None

class DealActionResponse(Model):
    """Response to deal action"""
    success: bool
    message: str
    game_result: Optional[str] = None  # "won", "lost", "in_progress"
    final_amount: Optional[int] = None
    error: Optional[str] = None

class GameHistoryResponse(Model):
    """Response for game history"""
    game_id: str
    messages: List[Dict[str, Any]]
    final_result: Optional[str] = None
    total_winnings: Optional[int] = None

class HealthResponse(Model):
    """Health check response"""
    status: str
    agent: str
    timestamp: str

class ErrorResponse(Model):
    """Error response"""
    error: str
    details: Optional[str] = None
    timestamp: str

class ActiveGamesResponse(Model):
    """Response for active games list"""
    active_games: List[str]
    total_games: int
    timestamp: str
