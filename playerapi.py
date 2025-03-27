# playerapi.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config import settings
import logging

router = APIRouter(prefix="/player", tags=["player"])
logger = logging.getLogger(__name__)

# In-memory player state
players = {}

# Request and response schemas
class TurnRequest(BaseModel):
    pot_size: int
    current_bet: int
    player_cards: list[int] = []

class TurnResponse(BaseModel):
    action: str
    amount: int = 0

# Register a player (called externally at game start)
def register_player(player_id: str, balance: int = None):
    if balance is None:
        balance = settings.initial_balance
    players[player_id] = {
        "balance": balance,
        "in_game": True,
        "folded": False
    }
    logger.info(f"✅ Registered player {player_id} with balance {balance}")

# Health check
@router.get("/ping")
async def ping():
    return {"status": "ok", "message": "Player API is running"}

# Core decision logic
def decide_action(player_state: dict, pot_size: int, current_bet: int) -> dict:
    balance = player_state["balance"]

    if player_state.get("folded") or balance <= 0:
        return {"action": "fold"}

    if current_bet == 0:
        open_amount = max(1, int(balance * 0.1))
        return {"action": "bet", "amount": open_amount}

    pot_odds = current_bet / (pot_size if pot_size > 0 else 1)
    balance_risk = current_bet / balance

    if balance_risk > 0.5:
        return {"action": "fold"}

    if pot_odds > 0.5 and balance_risk < 0.2:
        return {"action": "bet", "amount": current_bet}

    return {"action": "bet", "amount": current_bet}

# Turn endpoint
@router.post("/{player_id}/turn", response_model=TurnResponse)
async def player_turn(player_id: str, turn: TurnRequest):
    if player_id not in players:
        raise HTTPException(status_code=404, detail="Player not found")

    player_state = players[player_id]
    decision = decide_action(player_state, turn.pot_size, turn.current_bet)
    action, amount = decision["action"], decision.get("amount", 0)

    logger.info(f"🎯 Player {player_id} decision: {action} {'₹' + str(amount) if action == 'bet' else ''}")

    if action == "bet":
        if amount > player_state["balance"]:
            raise HTTPException(status_code=400, detail="Bet exceeds balance")
        player_state["balance"] -= amount

    elif action == "fold":
        player_state["folded"] = True

    return {"action": action, "amount": amount}

# Optional manual control endpoints
@router.post("/{player_id}/bet")
async def place_bet(player_id: str, amount: int):
    if player_id not in players:
        raise HTTPException(status_code=404, detail="Player not found")
    if amount <= 0 or amount > players[player_id]["balance"]:
        raise HTTPException(status_code=400, detail="Invalid bet")
    players[player_id]["balance"] -= amount
    return {"status": "bet placed", "new_balance": players[player_id]["balance"]}

@router.post("/{player_id}/fold")
async def fold(player_id: str):
    if player_id not in players:
        raise HTTPException(status_code=404, detail="Player not found")
    players[player_id]["folded"] = True
    return {"status": "folded"}

@router.post("/{player_id}/show")
async def show(player_id: str):
    if player_id not in players:
        raise HTTPException(status_code=404, detail="Player not found")
    return {"status": "show initiated"}

