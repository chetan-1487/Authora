from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings


load_dotenv()

DATABASE_CONNECTION=os.getenv("DATABASE_URL")

class Settings(BaseSettings):
    SECRET_KEY: str = "supersecretkey"
    JWT_ALGORITHM: str = "HS256"

settings = Settings()