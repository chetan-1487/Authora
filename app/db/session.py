from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

DATABASE_CONNECTION_URL = settings.DATABASE_CONNECTION

if not DATABASE_CONNECTION_URL:
    raise ValueError(
        "Database connection string is missing. Please check your config file."
    )

async_engine = create_async_engine(DATABASE_CONNECTION_URL, echo=False)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
