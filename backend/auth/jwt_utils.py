from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from env import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_TIME

class JWTValidationError(Exception):
    pass


def create_access_token(subject: str, user_id: int) -> str:
    """Create a JWT signed with HS256 using configured secret.
    Expiration is interpreted as days (per env comment)."""
    if not JWT_SECRET_KEY:
        raise RuntimeError("JWT secret key not configured")
    expires = datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRATION_TIME)
    to_encode = {"sub": subject, "id": user_id, "exp": expires}
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise JWTValidationError(str(e)) from e
