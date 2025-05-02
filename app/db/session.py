from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_CONNECTION

DATABASE_CONNECTION_URL = DATABASE_CONNECTION

if not DATABASE_CONNECTION_URL:
    raise ValueError("Database connection string is missing. Please check your config file.")

engine = create_engine(DATABASE_CONNECTION_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
