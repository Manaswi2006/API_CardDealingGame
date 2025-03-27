# init.py
import logging
from fastapi import FastAPI
from playerapi import router as player_router
from pydantic_settings import BaseSettings

# UwU Config class for settings
class Settings(BaseSettings):
    dealer_url: str = "http://127.0.0.1:8000"
    initial_balance: int = 1000

    class Config:
        env_file = ".env"

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
    logger.info("🚀 Player API service started on port 8001 with dealer @ %s", settings.dealer_url)

# Optional: Run directly
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8001)

