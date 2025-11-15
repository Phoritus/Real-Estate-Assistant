from typing import Annotated
from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from starlette import status
from controller.user_controller import create_user
from controller.auth_controller import login_for_access_token
from auth.google_auth_controller import login_with_google, google_login_url, google_callback
from auth.facebook_auth_controller import (
    login_with_facebook,
    facebook_login_url,
    facebook_callback,
)
from auth.github_auth_controller import (
    login_with_github,
    github_login_url,
    github_callback,
)
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

@router.post("/login", response_model=Token)
async def login(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: dbSession, remember: bool = False):
    token = login_for_access_token(form_data, db, remember)
    
    # set token in a cookie
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        max_age=7*24*60*60 if remember else None,  # 7 days if remember is True
        samesite="lax",
        secure=False # in development only
    )
    
    return token

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response):
    # Clear the access token cookie
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=False # in development only
    )
    return {"detail": "Successfully logged out."}


# Google OAuth routes
@router.get("/google-login-url", status_code=status.HTTP_200_OK)
async def get_google_login_url():
    url = google_login_url()
    return {"url": url}

@router.get("/google-callback")
async def handle_google_callback(request: Request, db: dbSession):
    user_info = await google_callback(request)
    token = login_with_google(user_info, db)
    
    # Redirect to home and set token in cookie
    front_url = "http://localhost:5173"
    response = RedirectResponse(url=front_url, status_code=status.HTTP_302_FOUND)
    
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        max_age=7*24*60*60,  # 7 days
        samesite="lax",
        secure=False # in development only
    )
    return response

# Facebook OAuth routes
@router.get("/facebook-login-url", status_code=status.HTTP_200_OK)
async def get_facebook_login_url():
    url = facebook_login_url()
    return {"url": url}

@router.get("/facebook-callback")
async def handle_facebook_callback(request: Request, db: dbSession):
    user_info = await facebook_callback(request)
    token = login_with_facebook(user_info, db)

    front_url = "http://localhost:5173"
    response = RedirectResponse(url=front_url, status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        max_age=7*24*60*60,
        samesite="lax",
        secure=False
    )
    return response


# GitHub OAuth routes
@router.get("/github-login-url", status_code=status.HTTP_200_OK)
async def get_github_login_url():
    url = github_login_url()
    return {"url": url}

@router.get("/github-callback")
async def handle_github_callback(request: Request, db: dbSession):
    user_info = await github_callback(request)
    token = login_with_github(user_info, db)

    front_url = "http://localhost:5173"
    response = RedirectResponse(url=front_url, status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        max_age=7*24*60*60,
        samesite="lax",
        secure=False
    )
    return response