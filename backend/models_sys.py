from pydantic import BaseModel
from typing import List

class UserBase(BaseModel):
    username: str
    email: str
    password: str