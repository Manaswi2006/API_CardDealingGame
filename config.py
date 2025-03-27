# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    dealer_url: str = "http://127.0.0.1:8000"
    initial_balance: int = 1000

    class Config:
        env_file = ".env"

settings = Settings()
