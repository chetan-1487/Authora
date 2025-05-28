from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv(override=True)

IS_DEVELOPMENT = os.getenv("IS_DEVELOPMENT", "false").lower() == "true"


class Settings(BaseSettings):
    SECRET_KEY: str = "supersecretkey"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    DATABASE_CONNECTION: str
    IS_DEVELOPMENT: bool = IS_DEVELOPMENT

    MAX_FILE_SIZE_MB: int = 5
    REGION: str
    aws_access_key_id: str
    aws_secret_access_key: str
    LOCALSTACK_ENDPOINT: str = "http://localhost:4566"

    class Config:
        env_file = ".env"


settings = Settings()
