import re
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import validates

Base = declarative_base()
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

class userSchema(Base):
    __tablename__ = 'users'

    id = Column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    username = Column(
        String
    )
    lastname = Column(
        String
    )
    email = Column(
        String, unique=True, index=True, nullable=False
    )
    password = Column(
        String, nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # --- Validators ---
    @validates("email")
    def validate_email(self, key, value: str) -> str:
        if value is None:
            raise ValueError("Email is required")
        email = value.strip().lower()
        if not EMAIL_REGEX.match(email):
            raise ValueError("Invalid email format")
        return email
  
class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str
    new_password_confirm: str

class UserBase(BaseModel):
    username: str
    lastname: str
    email: EmailStr
    password: str