#!/usr/bin/env python3
"""
Demo script showing the AI decision-making banker agent in action
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_ai_decisions():
    """Demonstrate the AI decision-making capabilities."""
    print("🤖 AI Decision-Making Banker Agent Demo 🤖")
    print("=" * 50)
    
    try:
        from hyperon import MeTTa
        from metta.knowledge import initialize_banker_knowledge
        from metta.banker_rag import BankerRAG
        from metta.utils import process_banker_query, LLM
        
        # Initialize the system
        metta = MeTTa()
        initialize_banker_knowledge(metta)
        rag = BankerRAG(metta)
        
        # Use the real LLM (you'll need to set up your API key)
        llm = LLM()
        
        # Demo scenarios
        demo_scenarios = [
            {
                "message": "Hello there!",
                "description": "Casual greeting - should be conversation",
                "cards": [1000, 5000, 10000, 500000, 1000000],
                "round": 1
            },
            {
                "message": "What's your offer?",
                "description": "Direct request for offer - should make offer",
                "cards": [1000, 5000, 10000, 500000, 1000000],
                "round": 1
            },
            {
                "message": "That's really cool!",
                "description": "Casual comment - should be conversation",
                "cards": [1000, 5000, 10000, 500000, 1000000],
                "round": 2
            },
            {
                "message": "I want to negotiate",
                "description": "Ready to negotiate - should make offer",
                "cards": [1000, 5000, 10000, 500000, 1000000],
                "round": 2
            },
            {
                "message": "Thanks for the game",
                "description": "Gratitude - AI will decide based on context",
                "cards": [1000, 5000, 10000, 500000, 1000000],
                "round": 3
            }
        ]
        
        for i, scenario in enumerate(demo_scenarios, 1):
            print(f"\n🎯 Scenario {i}: {scenario['description']}")
            print(f"Player says: '{scenario['message']}'")
            print(f"Remaining cards: {scenario['cards']}")
            print(f"Round: {scenario['round']}")
            print("-" * 40)
            
            try:
                # Process the query
                response = process_banker_query(
                    scenario['message'],
                    rag,
                    llm,
                    scenario['cards'],
                    [],  # burnt_cards
                    scenario['round']
                )
                
                # Display the response
                if response.get('offer') is not None:
                    print(f"🤖 AI Decision: OFFER")
                    print(f"💰 Offer: ${response['offer']:,}")
                    print(f"💬 Message: {response['humanized_answer']}")
                else:
                    print(f"🤖 AI Decision: CONVERSATION")
                    print(f"💬 Message: {response['humanized_answer']}")
                
            except Exception as e:
                print(f"❌ Error processing scenario: {e}")
                print("This might be due to missing API key or network issues")
        
        print("\n🎉 Demo completed!")
        print("\nKey Features Demonstrated:")
        print("✅ AI intelligently decides when to make offers vs chat")
        print("✅ Context-aware decision making")
        print("✅ Natural conversation flow")
        print("✅ Engaging personality maintained")
        print("✅ Proper offer calculation when needed")
        
    except Exception as e:
        print(f"❌ Error setting up demo: {e}")
        print("\nNote: This demo requires a valid API key for the LLM service.")
        print("Make sure your .env file has the correct API key configured.")

def main():
    """Run the demo."""
    demo_ai_decisions()

if __name__ == "__main__":
    main()
