
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging
import random
import requests

router = APIRouter(prefix="/player", tags=["player"])
logger = logging.getLogger(__name__)
DEALER_API_URLl = "http://192.168.43.238:8000/docs#/"
PLAYER_API_URL = "http://127.0.0.1:8001"

# Card-related constants
SUITS = ['H', 'D', 'C', 'S']  # Hearts, Diamonds, Clubs, Spades
VALUES = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

# Additional Models
class PlayerCards(BaseModel):
    cards: List[str]

class PotStatus(BaseModel):
    pot: float = 0.0

# In-memory player state
players = {}

class PlayerState:
    def _init_(self, name: str, balance: float = 100.0):
        self.name = name
        self.balance = balance
        self.cards: List[str] = []
        self.is_active = True

    def assign_cards(self, cards: List[str]):
        self.cards = cards

def generate_card() -> str:
    """Generate a random card in the format '2D', 'AD', '10H', etc."""
    value = random.choice(VALUES)
    suit = random.choice(SUITS)
    return f"{value}{suit}"

@router.post("/join_game")
async def join_game(request: dict):
    try:
        name = request.get("name")
        if not name:
            raise ValueError("Player name is required")
        
        # Create player state
        players[name] = PlayerState(name)
        
        # Generate initial cards
        initial_cards = [generate_card() for _ in range(3)]
        players[name].assign_cards(initial_cards)
        
        # Notify dealer about joining
        try:
            response = requests.post(f"{DEALER_API_URLl}/join_game", json={
                "name": name,
                "host_url": PLAYER_API_URL
            })
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to notify dealer: {e}")
            raise HTTPException(status_code=500, detail="Could not join game")
        
        logger.info(f"✅ Player {name} joined the game with cards {initial_cards}")
        
        return {
            "status": "joined", 
            "player": name, 
            "cards": initial_cards
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{player_id}/turn")
async def player_turn(player_id: str, request: dict):
    # Extract parameters
    pot_size = request.get('pot', 0)
    current_bet = request.get('current_bet', 0)
    
    if player_id not in players:
        raise HTTPException(status_code=404, detail="Player not found")

    player = players[player_id]
    
    # If player is not active, automatically fold
    if not player.is_active:
        return {"action": "fold"}

    # Simple decision logic
    # Randomly choose between bet, fold, and show
    actions = ['bet', 'fold', 'show']
    
    # Bias towards betting if player has good cards
    # This is a very simple heuristic and can be made more sophisticated
    good_card_values = ['10', 'J', 'Q', 'K', 'A']
    good_card_count = sum(1 for card in player.cards if any(val in card for val in good_card_values))
    
    if good_card_count >= 2:
        actions = ['bet', 'bet', 'show', 'fold']  # More likely to bet or show
    
    action = random.choice(actions)
    
    # Determine bet amount
    if action == 'bet':
        # Bet between 10% to 30% of current bet or a minimum of 10
        amount = max(10, int(current_bet * random.uniform(0.1, 0.3)))
        result = {"action": "bet", "amount": amount}
    elif action == 'show':
        result = {"action": "show"}
    else:
        result = {"action": "fold"}
    
    logger.info(f"🎯 Player {player_id} decision: {result}")
    
    return result

@router.get("/{player_id}/cards")
async def get_player_cards(player_id: str):
    if player_id not in players:
        raise HTTPException(status_code=404, detail="Player not found")
    
    return PlayerCards(cards=players[player_id].cards)

@router.get("/pot")
async def get_pot_status():
    try:
        # Fetch pot status from dealer
        response = requests.get(f"{DEALER_API_URLl}/pot")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch pot status: {e}")
        return PotStatus()