from typing import Annotated
from fastapi import Request, HTTPException
from env import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
import httpx
from urllib.parse import urlencode
from controller.auth_controller import create_access_token
from database.postgresdb import dbSession
from models.auth_model import Token
from controller.user_controller import create_user
from models.user_model import userSchema, UserBase
import secrets

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET or not GOOGLE_REDIRECT_URI:
    raise ValueError("Google OAuth2 credentials are not set in environment variables.")
  
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

def google_login_url() -> str:
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return url
  
async def google_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided.")
    
    # Exchange code for tokens
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    async with httpx.AsyncClient() as client:
        token_response = await client.post(GOOGLE_TOKEN_URL, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        access_token = tokens.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to obtain access token from Google.")
        
        # Fetch user info
        headers = {"Authorization": f"Bearer {access_token}"}
        userinfo_response = await client.get(GOOGLE_USERINFO_URL, headers=headers)
        userinfo_response.raise_for_status()
        user_info = userinfo_response.json()
        
        # Here you would typically create or fetch the user from your database
        # and create a session or JWT for them.
        
        return user_info  # For demonstration, returning user info directly
    

def login_with_google(user_info: dict, db: dbSession, remember: bool = False) -> Token:
    """Find or create a user from Google profile, then issue a JWT.

    For new users, we generate a random placeholder password since the DB schema
    requires a non-null password. Regular sign-in will still go through Google.
    """
    email = user_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not found in Google user info.")

    # Look up by email directly (no password verification for OAuth)
    user = db.query(userSchema).filter(userSchema.email == email).first()

    if not user:
        username = user_info.get("given_name") or (email.split("@")[0])
        lastname = user_info.get("family_name") or ""
        temp_password = secrets.token_urlsafe(12)  # placeholder
        new_user = UserBase(username=username, lastname=lastname, email=email, password=temp_password)
        user = create_user(new_user, db)["data"]["user"]

    access_token = create_access_token(subject=user.email, user_id=user.id)
    return Token(access_token=access_token, token_type="bearer")