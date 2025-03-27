# init.py
import logging
from fastapi import FastAPI
from playerapi import router as player_router
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize app
app = FastAPI(title="Teen Patti Player API", version="1.0")
app.include_router(player_router)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Player API service started on port 8001")

# Optional: To run standalone
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8001)

