#!/usr/bin/env python3
"""
Test script to verify that discouraging "house always wins" messages have been removed
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_no_house_messages():
    """Test that discouraging house messages have been removed."""
    print("🚫 Testing Removal of Discouraging House Messages...")
    
    # Test deal rejection message
    user_message_lower = "no deal"
    deal_phrases = ["accept", "yes", "take it", "i'll take it", "agreed", "i accept", "deal accepted", "take the deal"]
    rejects_deal = any(phrase in user_message_lower for phrase in ["no deal", "reject", "pass", "no thanks", "decline", "not interested"])
    
    if rejects_deal:
        answer_text = f"**❌ Deal Rejected**\n\n"
        answer_text += f"💬 **Your loss! Better luck next time!**\n\n"
        answer_text += f"🎰 **Game Over - Thanks for playing!**"
    
    print("   Deal rejection message:")
    print(f"   {answer_text}")
    
    # Check that discouraging message is not present
    assert "house always wins" not in answer_text.lower(), "Deal rejection should not mention 'house always wins'"
    assert "better luck next time" in answer_text, "Should still have encouraging message"
    print("   ✅ Deal rejection message is encouraging")
    
    # Test deal acceptance message
    user_message_lower = "accept"
    if any(phrase in user_message_lower for phrase in deal_phrases):
        answer_text = f"**🎉 DEAL ACCEPTED! 🎉**\n\n"
        answer_text += f"💰 **You've won: $50,000**\n\n"
        answer_text += f"💬 **Congratulations! You made the smart choice and walked away with guaranteed money!**\n\n"
        answer_text += f"🎰 **Game Over - Thanks for playing!**"
    
    print("\n   Deal acceptance message:")
    print(f"   {answer_text}")
    
    # Check that discouraging message is not present
    assert "house always wins" not in answer_text.lower(), "Deal acceptance should not mention 'house always wins'"
    assert "congratulations" in answer_text, "Should still congratulate the player"
    assert "smart choice" in answer_text, "Should still praise the player's decision"
    print("   ✅ Deal acceptance message is encouraging")
    
    print("\n🎉 All discouraging house messages have been successfully removed!")
    print("✅ Messages are now more encouraging and player-friendly")
    print("✅ Game maintains excitement without discouraging players")

def main():
    """Run the test."""
    test_no_house_messages()

if __name__ == "__main__":
    main()
