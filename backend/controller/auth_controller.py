from fastapi import Depends, status, HTTPException, Cookie
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from models import user_model, auth_model
from database.postgresdb import dbSession
from sqlalchemy import select
from env import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_TIME
from datetime import datetime, timedelta, timezone
from typing import Annotated
import logging
from middlewares.exceptions import AuthenticationError, AuthenticationWithCookie
from models.auth_model import Token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")  # Include prefix so docs/forms work
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # Password hashing context

  
def create_access_token(subject: str, user_id: int, remember: bool = False) -> str:
    """Create a JWT signed with HS256 using configured secret.
    Expiration is interpreted as days (per env comment)."""
    if not JWT_SECRET_KEY:
        raise RuntimeError("JWT secret key not configured")
    expires = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRATION_TIME if not remember else JWT_EXPIRATION_TIME * 24 * 7)
    to_encode = {"sub": subject, "id": user_id, "exp": expires}
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

async def authenticate_user(email: str, password: str, db: dbSession) -> user_model.userSchema | bool:
    result = await db.execute(
        select(user_model.userSchema).where(user_model.userSchema.email == email)
    )
    user = result.scalar_one_or_none()
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

def get_token_from_cookie(access_token: str | None = Cookie(default=None)) -> str:
    if not access_token:
        raise AuthenticationWithCookie()
    return access_token

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)



def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)



async def get_current_user(token: Annotated[str, Depends(get_token_from_cookie)], db: dbSession) -> user_model.userSchema:
    try:
        token_data = verify_token(token)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result = await db.execute(
        select(user_model.userSchema).where(user_model.userSchema.id == token_data.user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user



CurrentUser = Annotated[user_model.userSchema, Depends(get_current_user)]



async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: dbSession = None, remember: bool = False) -> Token:
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        logging.warning(f"Authentication failed for user: {form_data.username}")
        raise AuthenticationError()
    access_token = create_access_token(subject=user.email, user_id=user.id, remember=remember)
    logging.info(f"User {form_data.username} authenticated successfully.")
    return Token(access_token=access_token, token_type="bearer")


