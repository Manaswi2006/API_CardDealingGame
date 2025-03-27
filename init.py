# init.py
import logging
from fastapi import FastAPI
from playerapi import router as player_router
import uvicorn

# UwU Config class for settings
class Settings:
    dealer_url: str = "http://192.168.43.238:8000/docs#/"
    player_url: str = "http://127.0.0.1:8001"
    initial_balance: int = 1000

settings = Settings()

# Logging setup ~nya
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# App init uwu
app = FastAPI(title="Teen Patti Player API", version="1.0")
app.include_router(player_router)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Player API service started on %s with dealer @ %s", settings.player_url, settings.dealer_url)

if __name__ == "__main__":
    uvicorn.run("init:app", host="0.0.0.0", port=8001, reload=True)
