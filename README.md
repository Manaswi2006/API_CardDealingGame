# 🎮 Teen Patti Player API - FastAPI Based Multiplayer Bot

This is the **Player API** service for a multiplayer Teen Patti game built with **FastAPI**.  
It handles individual player logic including:
- Bet / Fold / Show actions
- Balance management
- Adaptive decision-making based on pot odds & risk
- Integration with a centralized dealer API

---

## 📦 Project Structure

```
├── init.py              # FastAPI app + settings
├── playerapi.py         # Core player game logic and API endpoints
├── README.md            # You're here :)
└── requirements.txt     # Dependencies (optional)
```

---

## 🚀 How to Run

### 1. Install Requirements

```bash
pip install fastapi uvicorn pydantic-settings
```

### 2. Run the API

```bash
uvicorn init:app --reload --port 8001
```

> Make sure the dealer API is also running (default: `http://127.0.0.1:8000`)

---

## 🔧 API Endpoints

### `GET /player/ping`

Health check endpoint to verify the player service is live.

---

### `POST /player/{player_id}/turn`

**Input:**
```json
{
  "pot_size": 100,
  "current_bet": 20,
  "player_cards": [5, 10, 11]
}
```

**Output:**
```json
{
  "action": "bet",
  "amount": 20
}
```

Makes a move (bet, fold, or show) based on game state and player balance.

---

### `POST /player/{player_id}/bet`

Force a bet for a specific player.

### `POST /player/{player_id}/fold`

Manually fold a player.

### `POST /player/{player_id}/show`

Trigger a showdown.

---

## 🧠 Adaptive Decision-Making

The bot evaluates:
- **Pot odds** (risk vs reward)
- **Balance risk** (how much of its balance it must bet)
- And adapts its behavior accordingly.

Basic strategy:
- Bets when pot odds are favorable.
- Folds when the bet exceeds 50% of balance.
- Opens betting if no one has bet yet.

---

## 🛡️ Security & Scaling Notes

- Use unique `player_id`s to isolate state.
- For real-money games, move state to a secure DB or Redis.
- Enable API key auth between player and dealer services in production.
- Avoid using floats for currency — use `int` (e.g., cents/paise).

---

## 🐍 Built With

- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/usage/pydantic_settings/)
- Uvicorn

---

## 🧪 Example Usage (cURL)

```bash
curl -X POST http://127.0.0.1:8001/player/player123/turn \
    -H "Content-Type: application/json" \
    -d '{"pot_size": 150, "current_bet": 30, "player_cards": [7, 8, 12]}'
```

---

## 🤝 Author

Built with ♥ by an intermediate FastAPI dev building smart, scalable card bots 🎴  
Drop a star ⭐ if it helped you, or fork and make your own bot army.

---
