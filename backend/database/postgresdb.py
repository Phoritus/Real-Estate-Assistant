from typing import Annotated
from fastapi.params import Depends
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from env import DB_URL
import os


def _build_engine(url: str):
    if url.startswith("sqlite"):
        return create_engine(url, future=True, connect_args={"check_same_thread": False})
    return create_engine(url, future=True)


# Resolve database URL with safe fallback for local dev/tests
DATABASE_URL = DB_URL or os.getenv("DATABASE_URL") or "sqlite:///./dev.db"
if not DB_URL:
    print("[database] Warning: DATABASE_URL not set. Falling back to sqlite:///./dev.db")

print("Connecting database...📑")
engine = _build_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
print("Database connected.✅")



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


dbSession = Annotated[Session, Depends(get_db)]