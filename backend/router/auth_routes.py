from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from controller.user_controller import create_user
from controller.auth_controller import login_for_access_token
from models.auth_model import Token
from models.user_model import UserBase
from database.postgresdb import dbSession


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserBase, db: dbSession):
    return create_user(user, db)

@router.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: dbSession):
    return login_for_access_token(form_data, db)
