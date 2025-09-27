# 🎰 Banker Agent REST API

A REST API implementation for the AI Banker Agent that enables frontend communication for a Deal or No Deal style game.

## 🏗️ Architecture Overview

```
Frontend (HTML/React/Vue) 
    ↕ HTTP REST API
uAgents Banker API Server
    ↕
Core Services
├── MeTTa Knowledge Graph (Banker Logic)
├── ASI:One LLM (Response Generation)
├── Game State Management (In-Memory)
└── Chat History Storage
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r api_requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file:
```env
ASI_ONE_API_KEY=your_asi_one_api_key_here
```

### 3. Start the API Server

```bash
python banker_api_server.py
```

The server will start on `http://localhost:8009`

### 4. Test the API

```bash
python test_api.py
```

### 5. Open Frontend

Open `frontend_example.html` in your browser to see the full game interface.

## 📡 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/start-game` | Start a new game |
| `POST` | `/chat` | Send message to banker |
| `POST` | `/update-game-state` | Update game state |
| `GET` | `/game-history/{game_id}` | Get chat history |
| `GET` | `/health` | Health check |
| `GET` | `/active-games` | List active games |

### Request/Response Examples

#### Start Game
```bash
curl -X POST http://localhost:8009/start-game \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "game_id": "123e4567-e89b-12d3-a456-426614174000",
  "game_state": {
    "game_id": "123e4567-e89b-12d3-a456-426614174000",
    "round": 1,
    "remaining_cards": [1, 5, 10, 25, 50, 100, 500, 1000, 2500, 5000, 10000, 25000, 50000, 75000, 100000, 200000, 300000, 400000, 500000, 750000, 1000000],
    "burnt_cards": [],
    "selected_case": null,
    "current_offer": 50000,
    "expected_value": 250000,
    "house_edge": 0.8,
    "status": "active"
  },
  "banker_message": "🎯 Round 1 Offer\n\n💰 My Offer: $50,000\n\n💬 Welcome to the game!",
  "success": true
}
```

#### Chat with Banker
```bash
curl -X POST http://localhost:8009/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "That offer is too low!",
    "game_id": "123e4567-e89b-12d3-a456-426614174000"
  }'
```

**Response:**
```json
{
  "banker_response": {
    "message": "🎯 Round 1 Offer\n\n💰 My Offer: $45,000\n\n💬 I understand your concern, but this is a fair offer considering the risks!",
    "offer": 45000,
    "game_state": { ... },
    "message_type": "offer",
    "sentiment": "aggressive"
  },
  "success": true
}
```

## 🎮 Frontend Integration

### JavaScript Example

```javascript
// Start a new game
async function startGame() {
  const response = await fetch('http://localhost:8009/start-game', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({})
  });
  const data = await response.json();
  return data;
}

// Send message to banker
async function sendMessage(gameId, message) {
  const response = await fetch('http://localhost:8009/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: message,
      game_id: gameId
    })
  });
  const data = await response.json();
  return data;
}
```

### React Example

```jsx
import React, { useState, useEffect } from 'react';

function BankerGame() {
  const [gameId, setGameId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [gameState, setGameState] = useState(null);

  const startGame = async () => {
    const response = await fetch('/api/start-game', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    const data = await response.json();
    setGameId(data.game_id);
    setGameState(data.game_state);
    setMessages([{ sender: 'banker', message: data.banker_message }]);
  };

  const sendMessage = async (message) => {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message,
        game_id: gameId
      })
    });
    const data = await response.json();
    setMessages(prev => [...prev, 
      { sender: 'user', message: message },
      { sender: 'banker', message: data.banker_response.message }
    ]);
    setGameState(data.banker_response.game_state);
  };

  return (
    <div>
      {!gameId ? (
        <button onClick={startGame}>Start Game</button>
      ) : (
        <div>
          <div className="game-state">
            <h3>Round {gameState?.round}</h3>
            <p>Remaining Cards: {gameState?.remaining_cards?.length}</p>
            {gameState?.current_offer && (
              <p>Current Offer: ${gameState.current_offer.toLocaleString()}</p>
            )}
          </div>
          <div className="chat">
            {messages.map((msg, i) => (
              <div key={i} className={`message ${msg.sender}`}>
                {msg.message}
              </div>
            ))}
          </div>
          <input 
            type="text" 
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                sendMessage(e.target.value);
                e.target.value = '';
              }
            }}
          />
        </div>
      )}
    </div>
  );
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ASI_ONE_API_KEY` | API key for ASI:One LLM | Yes |
| `PORT` | Server port (default: 8009) | No |

### Game Configuration

The game uses the following default configuration:

- **Total Cards**: 20 cards with values from $1 to $1,000,000
- **House Edge**: 20% early rounds, 15% mid rounds, 10% late rounds
- **Sentiment Analysis**: Confident, desperate, aggressive, neutral
- **Psychology**: Dynamic pressure tactics based on round and player behavior

## 🧪 Testing

### Run Tests
```bash
python test_api.py
```

### Manual Testing with curl
```bash
# Health check
curl http://localhost:8009/health

# Start game
curl -X POST http://localhost:8009/start-game -H "Content-Type: application/json" -d '{}'

# Chat
curl -X POST http://localhost:8009/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello banker!", "game_id": "your-game-id"}'
```

## 📊 Data Models

### GameState
```python
{
  "game_id": "string",
  "round": "integer",
  "remaining_cards": ["integer"],
  "burnt_cards": ["integer"],
  "selected_case": "integer|null",
  "current_offer": "integer|null",
  "expected_value": "integer|null",
  "house_edge": "float|null",
  "status": "string"  # "active", "completed", "abandoned"
}
```

### BankerResponse
```python
{
  "message": "string",
  "offer": "integer|null",
  "game_state": "GameState",
  "message_type": "string",  # "text", "offer", "conversation"
  "sentiment": "string|null",
  "psychology": "string|null"
}
```

## 🚀 Production Deployment

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r api_requirements.txt

EXPOSE 8009
CMD ["python", "banker_api_server.py"]
```

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker banker_api_server:banker_agent
```

### Environment Setup

```bash
# Production environment variables
export ASI_ONE_API_KEY="your-production-key"
export PORT=8009
export REDIS_URL="redis://localhost:6379"  # For session storage
export DATABASE_URL="postgresql://user:pass@localhost/banker_db"  # For persistence
```

## 🔍 Monitoring & Debugging

### Health Check
```bash
curl http://localhost:8009/health
```

### Active Games
```bash
curl http://localhost:8009/active-games
```

### Game History
```bash
curl http://localhost:8009/game-history/{game_id}
```

## 🎯 Features

- ✅ **Real-time Chat**: Interactive conversation with AI banker
- ✅ **Game State Management**: Track rounds, cards, offers
- ✅ **Sentiment Analysis**: Dynamic responses based on player behavior
- ✅ **Psychology Engine**: MeTTa-powered negotiation tactics
- ✅ **RESTful API**: Standard HTTP endpoints for easy integration
- ✅ **Frontend Ready**: Complete HTML example included
- ✅ **Error Handling**: Comprehensive error responses
- ✅ **Health Monitoring**: Built-in health checks

## 🔮 Future Enhancements

- [ ] **WebSocket Support**: Real-time bidirectional communication
- [ ] **Database Persistence**: PostgreSQL for game history
- [ ] **Redis Caching**: Session management and performance
- [ ] **Authentication**: User accounts and game history
- [ ] **Analytics**: Player behavior tracking and insights
- [ ] **Multiplayer**: Multiple players in same game
- [ ] **Customization**: Configurable game rules and banker personality

## 📝 License

This project is part of the Fetch.ai uAgents ecosystem and follows the same licensing terms.
