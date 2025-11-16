import os
import re
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator, Annotated
from fastapi import Depends

# โหลด .env
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables.")

# Create the async engine by replacing the scheme
async_db_url = re.sub(r'^postgresql:', 'postgresql+asyncpg:', DATABASE_URL)
engine = create_async_engine(
    async_db_url,
    echo=True, # ตั้งเป็น False ตอนขึ้น Production
    pool_pre_ping=True # แนะนำให้เปิดไว้
)

# Create "Session Factory"
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False # Recommended to set False for async
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency ที่จะ inject AsyncSession เข้าไปใน endpoint
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
            
dbSession = Annotated[AsyncSession, Depends(get_db)]