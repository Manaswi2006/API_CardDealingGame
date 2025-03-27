#player api which is used to hadle player 
import requests
import logging
import random
from enum import Enum, auto
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Configuration
PLAYER_NAME = "Player1"
PLAYER_API_URL = "http://127.0.0.1:8001"
DEALER_API_URL = "http://127.0.0.1:8000"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()

class TurnType(str, Enum):
    BET = "bet"
    FOLD = "fold"
    SHOW = "show"

class TurnRequest(BaseModel):
    type: TurnType

class ThreePattiPlayer:
    def __init__(self, name: str):
        self.name = name
        self.balance = 0  # Initial balance will be set by dealer
        self.current_bet = 0
        self.cards = []

    def ping_dealer(self) -> bool:
        """Check if dealer is responsive"""
        try:
            response = requests.get(f"{DEALER_API_URL}/ping")
            return response.json().get("message") == "pong"
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            return False

    def get_initial_balance(self) -> float:
        """
        Get initial balance from dealer
        
        :return: Initial balance for the player
        """
        try:
            response = requests.get(f"{DEALER_API_URL}/initial_balance")
            self.balance = response.json().get("balance", 0)
            logger.info(f"Initial balance received: {self.balance}")
            return self.balance
        except Exception as e:
            logger.error(f"Failed to get initial balance: {e}")
            return 0

    def get_cards(self) -> list:
        """Fetch player's cards"""
        try:
            response = requests.get(f"{DEALER_API_URL}/show_cards")
            self.cards = response.json().get("cards", [])
            return self.cards
        except Exception as e:
            logger.error(f"Failed to get cards: {e}")
            return []

    def check_pot(self) -> float:
        """Check current pot amount"""
        try:
            response = requests.get(f"{DEALER_API_URL}/show_pot")
            return response.json().get("pot_amount", 0)
        except Exception as e:
            logger.error(f"Failed to check pot: {e}")
            return 0

    def make_turn(self, turn_type: TurnType) -> Dict[str, Any]:
        """
        Make a turn in the game
        
        :param turn_type: Type of turn (bet, fold, show)
        :return: Turn result
        """
        try:
            # Simulate game logic
            if turn_type == TurnType.BET:
                # Randomize bet amount, but ensure it doesn't exceed balance
                bet_amount = random.uniform(10, min(100, self.balance))
                self.current_bet += bet_amount
                self.balance -= bet_amount
                return {
                    "type": "bet",
                    "amount": bet_amount,
                    "remaining_balance": self.balance
                }
            
            elif turn_type == TurnType.FOLD:
                return {
                    "type": "fold",
                    "message": "Player has folded the hand"
                }
            
            elif turn_type == TurnType.SHOW:
                # Evaluate cards (simplified)
                return {
                    "type": "show",
                    "cards": self.cards,
                    "message": "Showing cards"
                }
            
        except Exception as e:
            logger.error(f"Turn error: {e}")
            raise HTTPException(status_code=500, detail=f"Turn error: {e}")

# Create player instance
player = ThreePattiPlayer(PLAYER_NAME)

@app.get("/ping")
async def ping():
    """Health check endpoint"""
    return {"message": "pong"}

@app.post("/turn")
async def take_turn(turn_request: TurnRequest):
    """
    Endpoint to make a turn in the game
    
    :param turn_request: Turn type (bet, fold, show)
    :return: Turn result
    """
    # First, ensure dealer is responsive
    if not player.ping_dealer():
        raise HTTPException(status_code=503, detail="Dealer not available")
    
    # Get initial balance if not already set
    if player.balance == 0:
        player.get_initial_balance()
    
    # Get cards if not already fetched
    if not player.cards:
        player.get_cards()
    
    # Check current pot
    current_pot = player.check_pot()
    
    # Make turn
    turn_result = player.make_turn(turn_request.type)
    
    return {
        "player": player.name,
        "turn": turn_result,
        "current_pot": current_pot
    }

