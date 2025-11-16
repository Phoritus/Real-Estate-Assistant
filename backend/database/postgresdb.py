from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import Annotated, AsyncGenerator
from fastapi import Depends
from env import DATABASE_URL

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

# Create a session factory
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session."""
    async with async_session() as session:
        yield session

dbSession = Annotated[AsyncSession, Depends(get_db)]

async def init_db():
    """Initialize the database connection."""
    async with engine.begin() as conn:
        await conn.run_sync(lambda conn: None)  # No-op to test connection