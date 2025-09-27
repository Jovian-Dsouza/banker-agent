from typing import List, Optional, Dict, Any
from datetime import datetime
from uagents import Model

# Base Models (define first to avoid circular dependencies)
class GameState(Model):
    """Game state information"""
    game_id: str
    round: int
    remaining_boxes: List[int]  # Values still in play
    burnt_boxes: List[int]  # Values eliminated
    selected_box: Optional[int] = None  # Player's chosen box value
    current_offer: Optional[int] = None
    expected_value: Optional[int] = None
    house_edge: Optional[float] = None
    status: str  # "active", "completed", "abandoned"
    entry_fee_paid: bool = False
    max_offer_limit: int = 165  # Maximum offer allowed

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

class EntryFeeRequest(Model):
    """Request to pay entry fee"""
    game_id: str
    payment_amount: int  # Should be 5 PYUSD
    payment_currency: str = "PYUSD"

class AcceptDealRequest(Model):
    """Request to accept a deal and cash out"""
    game_id: str
    offer_amount: int  # Must be <= $165

class FinalSelectionRequest(Model):
    """Request for final box selection"""
    game_id: str
    keep_original_box: bool  # True to keep original box, False to switch

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

class EntryFeeResponse(Model):
    """Response to entry fee payment"""
    success: bool
    message: str
    game_state: GameState
    error: Optional[str] = None

class AcceptDealResponse(Model):
    """Response to accepting a deal"""
    success: bool
    message: str
    final_amount: int
    game_result: str = "completed"
    error: Optional[str] = None

class FinalSelectionResponse(Model):
    """Response to final box selection"""
    success: bool
    message: str
    final_amount: int
    selected_box_value: int
    other_box_value: int
    game_result: str = "completed"
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
