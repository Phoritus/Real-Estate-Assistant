from fastapi import Request, HTTPException
from urllib.parse import urlencode
import httpx
import secrets

from env import (
    FACEBOOK_CLIENT_ID,
    FACEBOOK_CLIENT_SECRET,
    FACEBOOK_REDIRECT_URI,
)
from controller.auth_controller import create_access_token
from controller.user_controller import create_user
from database.postgresdb import dbSession
from models.user_model import userSchema, UserBase
from models.auth_model import Token


if not FACEBOOK_CLIENT_ID or not FACEBOOK_CLIENT_SECRET or not FACEBOOK_REDIRECT_URI:
    raise ValueError("Facebook OAuth credentials are not set in environment variables.")

FACEBOOK_AUTH_URL = "https://www.facebook.com/v18.0/dialog/oauth"
FACEBOOK_TOKEN_URL = "https://graph.facebook.com/v18.0/oauth/access_token"
FACEBOOK_USERINFO_URL = "https://graph.facebook.com/me"


def facebook_login_url() -> str:
    params = {
        "client_id": FACEBOOK_CLIENT_ID,
        "redirect_uri": FACEBOOK_REDIRECT_URI,
        "response_type": "code",
        "scope": "email,public_profile",
    }
    return f"{FACEBOOK_AUTH_URL}?{urlencode(params)}"


async def facebook_callback(request: Request) -> dict:
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided.")

    token_query = {
        "client_id": FACEBOOK_CLIENT_ID,
        "client_secret": FACEBOOK_CLIENT_SECRET,
        "redirect_uri": FACEBOOK_REDIRECT_URI,
        "code": code,
    }

    async with httpx.AsyncClient() as client:
        token_resp = await client.get(FACEBOOK_TOKEN_URL, params=token_query)
        token_resp.raise_for_status()
        token_json = token_resp.json()
        access_token = token_json.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to obtain access token from Facebook.")

        user_params = {
            "fields": "id,name,first_name,last_name,email",
            "access_token": access_token,
        }
        user_resp = await client.get(FACEBOOK_USERINFO_URL, params=user_params)
        user_resp.raise_for_status()
        return user_resp.json()


def login_with_facebook(user_info: dict, db: dbSession, remember: bool = False) -> Token:
    print("Facebook user info:", user_info)
    email = user_info.get("email")
    if not email:
        # Some Facebook accounts may not have email if permission not granted
        raise HTTPException(status_code=400, detail="Email not found in Facebook user info.")

    user = db.query(userSchema).filter(userSchema.email == email).first()
    if not user:
        username = user_info.get("first_name") or (email.split("@")[0])
        lastname = user_info.get("last_name") or ""
        temp_password = secrets.token_urlsafe(12)
        new_user = UserBase(username=username, lastname=lastname, email=email, password=temp_password)
        user = create_user(new_user, db)["data"]["user"]

    token = create_access_token(subject=user.email, user_id=user.id, remember=remember)
    return Token(access_token=token, token_type="bearer")