from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings

load_dotenv()

CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI=os.getenv("GOOGLE_REDIRECT_URI")

DATABASE_CONNECTION=os.getenv("DATABASE_URL")

class Settings(BaseSettings):
    SECRET_KEY: str = "supersecretkey"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    GOOGLE_CLIENT_ID:str=CLIENT_ID
    GOOGLE_CLIENT_SECRET:str=CLIENT_SECRET
    GOOGLE_REDIRECT_URI:str=REDIRECT_URI

    
settings = Settings()

