from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

# Models
class Card(BaseModel):
    rank: str
    suit: str
    name: str

class JoinGameRequest(BaseModel):
    name: str
    host_url: str

class BetRequest(BaseModel):
    name: str
    amount: float

class FoldRequest(BaseModel):
    name: str

class GameStatusResponse(BaseModel):
    is_active: bool
    pot: float
    current_turn: Optional[str]
    players: List[dict]

class EndGameResponse(BaseModel):
    message: str

router = APIRouter(prefix="/player", tags=["player"])
logger = logging.getLogger(__name__)

# In-memory player state
players = {}

# Player class aligned with models
class PlayerState:
    def __init__(self, name: str, balance: float = 100.0):
        self.name = name
        self.balance = balance
        self.cards: List[Card] = []
        self.current_bet = 0.0
        self.is_active = True

    def place_bet(self, amount: float) -> tuple[bool, Optional[str]]:
        if amount > self.balance:
            return False, "Insufficient balance."
        self.balance -= amount
        self.current_bet += amount
        return True, None

    def fold(self):
        self.is_active = False

# Register a player
def register_player(player_id: str, balance: float = 100.0):
    players[player_id] = PlayerState(player_id, balance)
    logger.info(f"✅ Registered player {player_id} with balance {balance}")

# Health check
@router.get("/ping")
async def ping():
    return {"status": "ok", "message": "Player API is running"}

# Core decision logic
def decide_action(player: PlayerState, pot_size: float, current_bet: float) -> dict:
    if not player.is_active or player.balance <= 0:
        return {"action": "fold"}

    # Initial bet scenario
    if current_bet == 0:
        open_amount = max(1, int(player.balance * 0.1))
        return {"action": "bet", "amount": open_amount}

    # Calculate risk and pot odds
    pot_odds = current_bet / (pot_size if pot_size > 0 else 1)
    balance_risk = current_bet / player.balance

    # Decision logic
    if balance_risk > 0.5:
        return {"action": "fold"}

    if pot_odds > 0.5 and balance_risk < 0.2:
        return {"action": "bet", "amount": current_bet}

    return {"action": "bet", "amount": current_bet}

# Join Game
@router.post("/join_game")
async def join_game(request: JoinGameRequest):
    try:
        register_player(request.name)
        return {"status": "joined", "player": request.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Player Turn
@router.post("/{player_id}/turn")
async def player_turn(player_id: str, pot_size: float, current_bet: float):
    if player_id not in players:
        raise HTTPException(status_code=404, detail="Player not found")

    player = players[player_id]
    decision = decide_action(player, pot_size, current_bet)
    action = decision["action"]
    amount = decision.get("amount", 0)

    logger.info(f"🎯 Player {player_id} decision: {action} {'₹' + str(amount) if action == 'bet' else ''}")

    if action == "bet":
        success, error = player.place_bet(amount)
        if not success:
            raise HTTPException(status_code=400, detail=error)

    elif action == "fold":
        player.fold()

    return {
        "action": action, 
        "amount": amount if action == "bet" else 0
    }

# Bet Endpoint
@router.post("/{player_id}/bet")
async def place_bet(player_id: str, request: BetRequest):
    if player_id not in players:
        raise HTTPException(status_code=404, detail="Player not found")
    
    player = players[player_id]
    success, error = player.place_bet(request.amount)
    
    if not success:
        raise HTTPException(status_code=400, detail=error)
    
    return {"status": "bet placed", "new_balance": player.balance}

# Fold Endpoint
@router.post("/{player_id}/fold")
async def fold(player_id: str):
    if player_id not in players:
        raise HTTPException(status_code=404, detail="Player not found")
    
    player = players[player_id]
    player.fold()
    return {"status": "folded"}

# Show Endpoint
@router.post("/{player_id}/show")
async def show(player_id: str):
    if player_id not in players:
        raise HTTPException(status_code=404, detail="Player not found")
    
    return {"status": "show initiated"}

# Game Status Endpoint
@router.get("/game_status")
async def get_game_status():
    return GameStatusResponse(
        is_active=True,  # This would be dynamically set in a real implementation
        pot=0.0,
        current_turn=None,
        players=[
            {
                "name": player.name, 
                "balance": player.balance, 
                "is_active": player.is_active
            } for player in players.values()
        ]
    )

# End Game Endpoint
@router.post("/end_game")
async def end_game():
    # Reset all players
    for player in players.values():
        player.balance = 100.0
        player.cards = []
        player.current_bet = 0.0
        player.is_active = True
    
    return "Game ended successfully"