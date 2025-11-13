from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from models import user_model, auth_model
from database.postgresdb import get_db
from sqlalchemy.orm import Session
from env import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_TIME
from datetime import datetime, timedelta, timezone
from typing import Annotated
import logging
from middlewares.exceptions import AuthenticationError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")  # Include prefix so docs/forms work
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # Password hashing context

  
def create_access_token(subject: str, user_id: int) -> str:
    """Create a JWT signed with HS256 using configured secret.
    Expiration is interpreted as days (per env comment)."""
    if not JWT_SECRET_KEY:
        raise RuntimeError("JWT secret key not configured")
    expires = datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRATION_TIME)
    to_encode = {"sub": subject, "id": user_id, "exp": expires}
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def authenticate_user(email: str, password: str, db: Session) -> user_model.userSchema | bool:
    user = db.query(user_model.userSchema).filter(user_model.userSchema.email == email).first()
    if not user or not verify_password(password, user.password):
        return False
    return user

def verify_token(token: str) -> auth_model.TokenData:
  try:
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    user_id: int = payload.get("id")
    return auth_model.TokenData(user_id=user_id)
  except JWTError as e:
    logging.warning(f"Token validation failed: {str(e)}")
    raise AuthenticationError()
    
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
  
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)) -> user_model.userSchema:
  return verify_token(token)

CurrentUser = Annotated[auth_model.TokenData, Depends(get_current_user)]

def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> auth_model.Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        logging.warning(f"Authentication failed for user: {form_data.username}")
        raise AuthenticationError()
    access_token = create_access_token(subject=user.email, user_id=user.id)
    logging.info(f"User {form_data.username} authenticated successfully.")
    return auth_model.Token(access_token=access_token, token_type="bearer")