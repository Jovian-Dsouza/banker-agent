#!/usr/bin/env python3
"""
Test script for the Banker API Server
Run this after starting the API server to test the endpoints
"""

import requests
import json
import time

API_BASE = "http://localhost:8009"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"✅ Health check: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_start_game():
    """Test starting a new game"""
    print("\n🎮 Testing start game...")
    try:
        response = requests.post(f"{API_BASE}/start-game", json={})
        data = response.json()
        
        if data.get("success"):
            print(f"✅ Game started: {data['game_id']}")
            print(f"💰 Banker message: {data['banker_message']}")
            return data['game_id']
        else:
            print(f"❌ Failed to start game: {data.get('error')}")
            return None
    except Exception as e:
        print(f"❌ Start game failed: {e}")
        return None

def test_chat(game_id, message):
    """Test chatting with banker"""
    print(f"\n💬 Testing chat: '{message}'")
    try:
        response = requests.post(f"{API_BASE}/chat", json={
            "message": message,
            "game_id": game_id
        })
        data = response.json()
        
        if data.get("success"):
            banker_response = data['banker_response']
            print(f"✅ Banker response: {banker_response['message']}")
            if banker_response.get('offer'):
                print(f"💰 Offer: ${banker_response['offer']:,}")
            return banker_response
        else:
            print(f"❌ Chat failed: {data.get('error')}")
            return None
    except Exception as e:
        print(f"❌ Chat failed: {e}")
        return None

def test_game_history(game_id):
    """Test getting game history"""
    print(f"\n📚 Testing game history for {game_id}...")
    try:
        response = requests.get(f"{API_BASE}/game-history/{game_id}")
        data = response.json()
        
        print(f"✅ Game history retrieved:")
        print(f"   Messages: {len(data['messages'])}")
        print(f"   Final result: {data.get('final_result', 'N/A')}")
        print(f"   Total winnings: ${data.get('total_winnings', 0):,}")
        return data
    except Exception as e:
        print(f"❌ Game history failed: {e}")
        return None

def main():
    """Run all tests"""
    print("🚀 Starting Banker API Tests")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("❌ API server is not running. Please start it first.")
        return
    
    # Test start game
    game_id = test_start_game()
    if not game_id:
        print("❌ Cannot continue without a game")
        return
    
    # Test various chat scenarios
    test_chat(game_id, "Hello banker!")
    test_chat(game_id, "What's your offer?")
    test_chat(game_id, "That's too low, I want more!")
    test_chat(game_id, "I accept the deal!")
    
    # Test game history
    test_game_history(game_id)
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()
