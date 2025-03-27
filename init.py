#connec the app to the their api 
import logging
import requests
from fastapi import FastAPI, HTTPException
import uvicorn

app = FastAPI()
PLAYER_NAME = "Player1"
PLAYER_API_URL = "http://127.0.0.1:8001"
DEALER_API_URL = "http://127.0.0.1:8000"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting Player API...")
    uvicorn.run(app, host="127.0.0.1", port=8001)