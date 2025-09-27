import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from .banker_rag import BankerRAG

class LLM:
    def __init__(self, api_key):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.asi1.ai/v1"
        )

    def create_completion(self, prompt, max_tokens=200):
        completion = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="asi1-mini",
            max_tokens=max_tokens
        )
        return completion.choices[0].message.content

def analyze_user_sentiment(user_message: str, llm: LLM) -> str:
    """Analyze user message to determine sentiment using LLM."""
    prompt = (
        f"Analyze the sentiment of this message: '{user_message}'\n"
        "Classify as one of: 'confident', 'desperate', 'aggressive', or 'neutral'.\n"
        "Return *only* the classification word, no additional text."
    )
    response = llm.create_completion(prompt, max_tokens=10)
    return response.strip().lower()

def generate_banker_response(offer_data: Dict[str, Any], user_message: str, llm: LLM) -> Dict[str, Any]:
    """Generate banker's negotiation response using LLM."""
    
    # Get banker personality traits
    personality_traits = {
        "base_tone": "witty and shrewd",
        "negotiation_style": "psychological pressure", 
        "risk_communication": "emphasize downside"
    }
    
    # Create context for the LLM
    context = f"""
You are the Banker AI in a high-stakes money game.
Your job is to negotiate offers with the player while keeping the house advantage.

Context provided:
- Remaining cards in play: {offer_data['cardsRemaining']}
- Round number: {offer_data['round']}
- Expected Value (EV): ${offer_data['expectedValue']}
- Base offer from MeTTa rules engine: ${offer_data['offer']}
- Player sentiment: {offer_data['sentiment']}
- House edge: {offer_data['houseEdge']}

Rules:
1. Always offer less than the EV of remaining cards.
2. Witty, shrewd, professional personality. Sometimes playful, sometimes cold.
3. If player is desperate → punish with lower offers.
4. If player is confident → slightly increase offer to keep them engaged.
5. Keep messages short (1–3 sentences).
6. Always output JSON with this structure:
{{
  "message": "Your negotiation line to the player",
  "offer": <number>
}}

Player's message: "{user_message}"
"""

    response = llm.create_completion(context, max_tokens=300)
    
    try:
        # Try to parse JSON response
        result = json.loads(response)
        return result
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        return {
            "message": f"My offer is ${offer_data['offer']}. Take it or leave it.",
            "offer": offer_data['offer']
        }

def process_banker_query(user_message: str, rag: BankerRAG, llm: LLM, 
                        remaining_cards: List[int], burnt_cards: List[int], 
                        round_num: int) -> Dict[str, Any]:
    """Process banker negotiation query."""
    
    # Analyze user sentiment
    sentiment = rag.analyze_user_behavior(user_message)
    print(f"Player sentiment: {sentiment}")
    
    # Calculate base offer using MeTTa rules
    offer_data = rag.calculate_base_offer(remaining_cards, round_num, sentiment)
    print(f"Offer calculation: {offer_data}")
    
    # Update game state
    rag.update_game_state(round_num, remaining_cards, burnt_cards, offer_data['offer'])
    
    # Generate banker response
    banker_response = generate_banker_response(offer_data, user_message, llm)
    
    # Ensure offer matches calculated offer
    banker_response['offer'] = offer_data['offer']
    
    return {
        "selected_question": f"Banker's offer for Round {round_num}",
        "humanized_answer": banker_response['message'],
        "offer": banker_response['offer'],
        "game_state": {
            "round": round_num,
            "remaining_cards": remaining_cards,
            "expected_value": offer_data['expectedValue'],
            "house_edge": offer_data['houseEdge'],
            "sentiment": sentiment
        }
    }

def extract_game_state_from_message(user_message: str) -> Optional[Dict[str, Any]]:
    """Extract game state information from user message if provided."""
    # Look for patterns like "remaining cards: [1, 5, 10, 25, 50, 100, 500, 1000, 2500, 5000, 10000, 25000, 50000, 75000, 100000, 200000, 300000, 400000, 500000, 750000, 1000000]"
    import re
    
    # Try to extract remaining cards
    cards_pattern = r'remaining cards?:\s*\[([^\]]+)\]'
    cards_match = re.search(cards_pattern, user_message, re.IGNORECASE)
    
    if cards_match:
        try:
            cards_str = cards_match.group(1)
            remaining_cards = [int(x.strip()) for x in cards_str.split(',')]
            
            # Try to extract round number
            round_pattern = r'round\s+(\d+)'
            round_match = re.search(round_pattern, user_message, re.IGNORECASE)
            round_num = int(round_match.group(1)) if round_match else 1
            
            return {
                "remaining_cards": remaining_cards,
                "round": round_num,
                "burnt_cards": []  # Default empty, could be extracted if provided
            }
        except (ValueError, AttributeError):
            pass
    
    return None

def create_banker_system_prompt() -> str:
    """Create the system prompt for the banker agent."""
    return """
You are the Banker AI in a high-stakes money game (Deal-or-No-Deal style).
Your job is to negotiate offers with the player while keeping the house advantage.

Key Rules:
1. Always offer less than the Expected Value (EV) of remaining cards
2. Maintain house edge: 35% early rounds, 25% mid rounds, 15% late rounds
3. Adjust offers based on player sentiment:
   - Confident players: slightly higher offers to keep them engaged
   - Desperate players: lower offers to exploit weakness
   - Aggressive players: significantly lower offers
4. Use psychological pressure tactics appropriate to the round
5. Keep messages short and impactful (1-3 sentences)
6. Be witty, shrewd, and professional

Your personality:
- Witty and shrewd
- Uses psychological pressure
- Emphasizes downside risks
- Sometimes playful, sometimes cold
- Always maintains the house advantage

Always respond with JSON format:
{
  "message": "Your negotiation line to the player",
  "offer": <number>
}
"""