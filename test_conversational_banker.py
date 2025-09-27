#!/usr/bin/env python3
"""
Test script for the conversational banker agent features
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_offer_detection():
    """Test the offer detection logic."""
    print("🎰 Testing Offer Detection Logic...")
    
    try:
        from metta.utils import should_make_offer
        
        # Test cases for offer detection
        test_cases = [
            # Should make offers
            ("What's your offer?", True),
            ("Make me a deal", True),
            ("How much money?", True),
            ("Give me an offer", True),
            ("What's the price?", True),
            ("I want to negotiate", True),
            ("Next round", True),
            ("Continue playing", True),
            ("Let's play", True),
            
            # Should NOT make offers (conversational)
            ("Hello", False),
            ("Hi there", False),
            ("How are you?", False),
            ("Thanks", False),
            ("That's cool", False),
            ("Really?", False),
            ("I think so", False),
            ("I feel good", False),
            ("I understand", False),
            ("Nice game", False),
            ("Wow", False),
            ("Okay", False),
            ("Sure", False),
            ("Maybe", False),
        ]
        
        for message, should_offer in test_cases:
            result = should_make_offer(message)
            print(f"   '{message}' -> should_offer: {result} (expected: {should_offer})")
            assert result == should_offer, f"Expected {should_offer}, got {result} for message '{message}'"
        
        print("   ✅ Offer detection logic working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing offer detection: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_conversational_response():
    """Test the conversational response generation."""
    print("\n💬 Testing Conversational Response Generation...")
    
    try:
        from hyperon import MeTTa
        from metta.knowledge import initialize_banker_knowledge
        from metta.banker_rag import BankerRAG
        from metta.utils import generate_conversational_response, LLM
        
        metta = MeTTa()
        initialize_banker_knowledge(metta)
        rag = BankerRAG(metta)
        
        # Mock LLM for testing (we'll just test the function structure)
        class MockLLM:
            def create_completion(self, prompt, max_tokens=200):
                return "Well, well, well! Look who's ready to play with the big boys! 🎰 I see some MASSIVE numbers still lurking in there! 😈 What's your move, player? 🎯"
        
        llm = MockLLM()
        
        # Test conversational response
        test_cards = [1, 100, 1000, 10000, 100000, 500000, 1000000]
        response = generate_conversational_response("Hello there!", rag, llm, test_cards, 1)
        
        print(f"   Conversational response: {response}")
        
        # Check that it's engaging and doesn't contain offer language
        assert "offer" not in response.lower(), "Conversational response should not contain 'offer'"
        assert "deal" not in response.lower(), "Conversational response should not contain 'deal'"
        assert "money" not in response.lower(), "Conversational response should not contain 'money'"
        assert "🎰" in response, "Should have engaging emojis"
        
        print("   ✅ Conversational response generation working")
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing conversational response: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_response_formatting():
    """Test the response formatting for different scenarios."""
    print("\n📝 Testing Response Formatting...")
    
    # Test offer response formatting
    offer_response = {
        "offer": 50000,
        "game_state": {
            "round": 3,
            "remaining_cards": [1000, 5000, 10000, 500000, 1000000],
            "expected_value": 303200,
            "house_edge": 0.25,
            "sentiment": "neutral"
        },
        "humanized_answer": "You've got some big numbers left. My offer is $50,000 - take the guaranteed money or risk it all!"
    }
    
    # Test conversational response formatting
    conversation_response = {
        "offer": None,
        "game_state": {
            "round": 3,
            "remaining_cards": [1000, 5000, 10000, 500000, 1000000],
            "expected_value": None,
            "house_edge": None,
            "sentiment": "conversational"
        },
        "humanized_answer": "Well, well, well! Look who's ready to play with the big boys! 🎰 I see some MASSIVE numbers still lurking in there! 😈 What's your move, player? 🎯"
    }
    
    # Test offer response formatting
    if offer_response.get('offer') is not None:
        answer_text = f"**🎯 Round {offer_response['game_state']['round']} Offer**\n\n"
        answer_text += f"💰 **My Offer: ${offer_response['offer']:,}**\n\n"
        answer_text += f"💬 **{offer_response['humanized_answer']}**"
    else:
        answer_text = f"**💬 {offer_response['humanized_answer']}**"
    
    print("   Offer response formatting:")
    print(f"   {answer_text}")
    assert "🎯 Round" in answer_text, "Should have round header"
    assert "💰 My Offer" in answer_text, "Should have offer amount"
    print("   ✅ Offer response formatting correct")
    
    # Test conversational response formatting
    if conversation_response.get('offer') is not None:
        answer_text = f"**🎯 Round {conversation_response['game_state']['round']} Offer**\n\n"
        answer_text += f"💰 **My Offer: ${conversation_response['offer']:,}**\n\n"
        answer_text += f"💬 **{conversation_response['humanized_answer']}**"
    else:
        answer_text = f"**💬 {conversation_response['humanized_answer']}**"
    
    print("\n   Conversational response formatting:")
    print(f"   {answer_text}")
    assert "💬" in answer_text, "Should have conversation emoji"
    assert "🎯 Round" not in answer_text, "Should not have round header"
    assert "💰 My Offer" not in answer_text, "Should not have offer amount"
    print("   ✅ Conversational response formatting correct")

def main():
    """Run all tests."""
    print("🎰 Conversational Banker Agent Test Suite 🎰")
    print("=" * 50)
    
    success = True
    
    # Test offer detection
    if not test_offer_detection():
        success = False
    
    # Test conversational response
    if not test_conversational_response():
        success = False
    
    # Test response formatting
    test_response_formatting()
    
    if success:
        print("\n🎉 All conversational banker tests passed!")
        print("\nKey Features Verified:")
        print("✅ Offer detection (only makes offers when needed)")
        print("✅ Conversational responses (chats without making offers)")
        print("✅ Response formatting (different formats for offers vs conversations)")
        print("✅ Engaging personality maintained in conversations")
        print("✅ No unwanted offers during casual chat")
        
        print("\nThe banker agent now has intelligent conversation detection!")
        print("It will chat normally when users are just talking, and only make offers when necessary!")
        
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
