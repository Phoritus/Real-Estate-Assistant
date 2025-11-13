from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from datetime import datetime, timezone
from passlib.context import CryptContext
from models import user_model
from models_sys import UserBase
from database.postgresdb import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from env import JWT_EXPIRATION_TIME
from auth.jwt_utils import create_access_token, decode_token, JWTValidationError

class Token(BaseModel):
    access_token: str
    token_type: str

user_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")  # Include prefix so docs/forms work
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # Password hashing context


@user_router.get("/")
async def get_users(db: Session = Depends(get_db)):
    db_users = db.query(user_model.userSchema).all()
    return {"users": db_users}


@user_router.get("/me")
async def read_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Return the currently authenticated user.

    Placed before '/{user_id}' to avoid FastAPI trying to parse 'me' as an int.
    """
    try:
        payload = decode_token(token)
    except JWTValidationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {e}")
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing subject")
    user = db.query(user_model.userSchema).filter(user_model.userSchema.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"user": user, "token_payload": payload}


@user_router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(user_model.userSchema).filter(user_model.userSchema.id == user_id).first()
    if db_user:
        return {"user": db_user}
    return {"message": "User not found"}


@user_router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    user.password = hashed_password
    db_user = user_model.userSchema(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    access_token = create_access_token(db_user.username, db_user.id)
    return { 
            "success": True,
            "data": {
                "user": db_user,
                "access_token": access_token
            }
        }


@user_router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(user_model.userSchema).filter(user_model.userSchema.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user.username, user.id)
    return {"access_token": access_token, "data": {"user": user}}


@user_router.put("/{user_id}")
async def update_user(user_id: int, user: UserBase, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    user.password = hashed_password
    db_user = db.query(user_model.userSchema).filter(user_model.userSchema.id == user_id).first()
    if db_user:
        for key, value in user.model_dump().items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
        return {"user": db_user}
    return {"message": "User not found"}


@user_router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(user_model.userSchema).filter(user_model.userSchema.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return {"message": "User deleted successfully"}
    return {"message": "User not found"}

