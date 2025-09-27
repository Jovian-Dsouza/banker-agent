#!/usr/bin/env python3
"""
Test script for the engaging banker agent features
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_engaging_features():
    """Test the engaging conversation features."""
    print("🎰 Testing Engaging Banker Features...")
    
    try:
        from hyperon import MeTTa
        from metta.knowledge import initialize_banker_knowledge
        from metta.banker_rag import BankerRAG
        
        metta = MeTTa()
        initialize_banker_knowledge(metta)
        rag = BankerRAG(metta)
        
        # Test conversation starters
        early_starter = rag.get_conversation_starter(1)
        mid_starter = rag.get_conversation_starter(3)
        late_starter = rag.get_conversation_starter(6)
        
        print(f"   Early game starter: {early_starter}")
        print(f"   Mid game starter: {mid_starter}")
        print(f"   Late game starter: {late_starter}")
        
        assert "🎰" in early_starter, "Early starter should have emoji"
        assert "💰" in mid_starter, "Mid starter should have emoji"
        assert "🎯" in late_starter, "Late starter should have emoji"
        print("   ✅ Conversation starters working")
        
        # Test drama phrases
        big_cards_phrase = rag.get_drama_phrase("big_cards")
        risk_phrase = rag.get_drama_phrase("risk_reminder")
        confidence_phrase = rag.get_drama_phrase("confidence_builder")
        
        print(f"   Big cards phrase: {big_cards_phrase}")
        print(f"   Risk phrase: {risk_phrase}")
        print(f"   Confidence phrase: {confidence_phrase}")
        
        assert "😈" in big_cards_phrase, "Big cards phrase should have emoji"
        assert "⚡" in risk_phrase, "Risk phrase should have emoji"
        assert "💪" in confidence_phrase, "Confidence phrase should have emoji"
        print("   ✅ Drama phrases working")
        
        # Test engaging context creation
        test_cards = [1, 100, 1000, 10000, 100000, 500000, 1000000]
        engaging_context = rag.create_engaging_context(test_cards, 2, "confident")
        
        print(f"   Engaging context: {engaging_context}")
        
        assert "MASSIVE" in engaging_context, "Should mention MASSIVE cards"
        assert "💰" in engaging_context, "Should have money emoji"
        assert "🎯" in engaging_context, "Should have target emoji"
        print("   ✅ Engaging context creation working")
        
        # Test personality traits
        traits = rag.get_banker_personality_traits()
        print(f"   Base tone: {traits['base_tone']}")
        print(f"   Negotiation style: {traits['negotiation_style']}")
        print(f"   Risk communication: {traits['risk_communication']}")
        
        assert "charismatic" in traits['base_tone'], "Should be charismatic"
        assert "casino dealer" in traits['negotiation_style'], "Should be casino dealer style"
        assert "tension" in traits['risk_communication'], "Should build tension"
        print("   ✅ Personality traits working")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing engaging features: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_drama_analysis():
    """Test the drama analysis of remaining cards."""
    print("\n🎭 Testing Drama Analysis...")
    
    try:
        from hyperon import MeTTa
        from metta.knowledge import initialize_banker_knowledge
        from metta.banker_rag import BankerRAG
        
        metta = MeTTa()
        initialize_banker_knowledge(metta)
        rag = BankerRAG(metta)
        
        # Test different card combinations
        test_cases = [
            {
                "cards": [1, 5, 10, 25, 50],
                "expected": "small",
                "description": "All small cards"
            },
            {
                "cards": [100000, 500000, 1000000],
                "expected": "big",
                "description": "All big cards"
            },
            {
                "cards": [1000, 5000, 10000, 50000, 100000],
                "expected": "medium",
                "description": "Mixed medium cards"
            }
        ]
        
        for test_case in test_cases:
            context = rag.create_engaging_context(test_case["cards"], 1, "neutral")
            print(f"   {test_case['description']}: {context}")
            
            if test_case["expected"] == "big":
                assert "MASSIVE" in context, f"Should mention MASSIVE for {test_case['description']}"
            elif test_case["expected"] == "small":
                assert "smaller amounts" in context, f"Should mention smaller amounts for {test_case['description']}"
            elif test_case["expected"] == "medium":
                assert "Decent numbers" in context, f"Should mention decent numbers for {test_case['description']}"
        
        print("   ✅ Drama analysis working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing drama analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🎰 Engaging Banker Agent Test Suite 🎰")
    print("=" * 50)
    
    success = True
    
    # Test engaging features
    if not test_engaging_features():
        success = False
    
    # Test drama analysis
    if not test_drama_analysis():
        success = False
    
    if success:
        print("\n🎉 All engaging banker tests passed!")
        print("\nKey Features Verified:")
        print("✅ Conversation starters for different rounds")
        print("✅ Drama-building phrases with emojis")
        print("✅ Engaging context creation")
        print("✅ Personality traits (charismatic, casino dealer)")
        print("✅ Drama analysis of remaining cards")
        print("✅ Emoji usage for engagement")
        
        print("\nThe banker agent is now much more engaging and conversational!")
        print("It will create drama, use emojis, and keep players engaged like a real TV game show host!")
        
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
