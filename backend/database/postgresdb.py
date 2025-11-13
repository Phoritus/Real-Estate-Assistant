from typing import Annotated
from fastapi.params import Depends
from pytest import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from env import DB_URL

if not DB_URL:
    raise ValueError("DATABASE_URL is not set in environment variables.")
engine = create_engine(DB_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
dbSession = Annotated[Session, Depends(get_db)]