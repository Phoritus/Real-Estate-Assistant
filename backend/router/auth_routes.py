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

def set_auth_cookie(response: Response, token: str, request: Request, max_age: int | None = None):
    """Set authentication cookie. Uses Partitioned+SameSite=None for HTTPS, relaxed for local HTTP dev."""
    is_https = request.url.scheme == "https"
    parts = [
        f"access_token={token}",
        "Path=/",
        "HttpOnly",
    ]
    if max_age:
        parts.append(f"Max-Age={max_age}")

    if is_https:
        parts.extend(["Secure", "SameSite=None", "Partitioned"])
    else:
        # Local dev over http cannot use Secure/None; fall back to Lax
        parts.append("SameSite=Lax")

    response.headers.append("Set-Cookie", "; ".join(parts))


def clear_auth_cookie(response: Response, request: Request):
    is_https = request.url.scheme == "https"
    parts = [
        "access_token=",
        "Path=/",
        "HttpOnly",
        "Max-Age=0",
    ]
    if is_https:
        parts.extend(["Secure", "SameSite=None", "Partitioned"])
    else:
        parts.append("SameSite=Lax")
    response.headers.append("Set-Cookie", "; ".join(parts))

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserBase, db: dbSession):
    return await create_user(user, db)

@router.post("/login", response_model=Token)
async def login(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: dbSession, remember: bool = False, request: Request | None = None):
    token = await login_for_access_token(form_data, db, remember)
    
    # Set token in cookie with Partitioned attribute
    max_age = 7*24*60*60 if remember else 24*60*60  # 7 days if remember, else 1 day
    # request will always be provided by FastAPI if in params
    if request is None:
        raise RuntimeError("Request is required for setting cookie attributes")
    set_auth_cookie(response, token.access_token, request, max_age)
    
    return token

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response, request: Request):
    clear_auth_cookie(response, request)
    return {"detail": "Successfully logged out."}


# Google OAuth routes
@router.get("/google-login-url", status_code=status.HTTP_200_OK)
async def get_google_login_url():
    url = google_login_url()
    return {"url": url}

@router.get("/google-callback")
async def handle_google_callback(request: Request, db: dbSession):
    user_info = await google_callback(request)
    token = await login_with_google(user_info, db)
    
    # Redirect to home and set token in cookie
    front_url = "https://real-estate-assistant-vert.vercel.app"
    response = RedirectResponse(url=front_url, status_code=status.HTTP_302_FOUND)
    
    # Set cookie with appropriate attributes based on scheme
    set_auth_cookie(response, token.access_token, request, 7*24*60*60)
    
    return response

# Facebook OAuth routes
@router.get("/facebook-login-url", status_code=status.HTTP_200_OK)
async def get_facebook_login_url():
    url = facebook_login_url()
    return {"url": url}

@router.get("/facebook-callback")
async def handle_facebook_callback(request: Request, db: dbSession):
    user_info = await facebook_callback(request)
    token = await login_with_facebook(user_info, db)

    front_url = "https://real-estate-assistant-vert.vercel.app"
    response = RedirectResponse(url=front_url, status_code=status.HTTP_302_FOUND)
    
    # Set cookie with appropriate attributes based on scheme
    set_auth_cookie(response, token.access_token, request, 7*24*60*60)
    
    return response


# GitHub OAuth routes
@router.get("/github-login-url", status_code=status.HTTP_200_OK)
async def get_github_login_url():
    url = github_login_url()
    return {"url": url}

@router.get("/github-callback")
async def handle_github_callback(request: Request, db: dbSession):
    user_info = await github_callback(request)
    token = await login_with_github(user_info, db)

    front_url = "https://real-estate-assistant-vert.vercel.app"
    response = RedirectResponse(url=front_url, status_code=status.HTTP_302_FOUND)
    
    # Set cookie with appropriate attributes based on scheme
    set_auth_cookie(response, token.access_token, request, 7*24*60*60)
    
    return response