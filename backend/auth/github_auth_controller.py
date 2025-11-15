from fastapi import Request, HTTPException
from urllib.parse import urlencode
import httpx
import secrets

from env import (
    GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET,
    GITHUB_REDIRECT_URI,
)
from controller.auth_controller import create_access_token
from controller.user_controller import create_user
from database.postgresdb import dbSession
from models.user_model import userSchema, UserBase
from models.auth_model import Token

if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET or not GITHUB_REDIRECT_URI:
    raise ValueError("GitHub OAuth credentials are not set in environment variables.")

GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USERINFO_URL = "https://api.github.com/user"

def github_login_url() -> str:
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "scope": "read:user user:email",
        "allow_signup": "true"
    }
    return f"{GITHUB_AUTH_URL}?{urlencode(params)}"
  
async def github_callback(request: Request) -> dict:
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided.")

    token_data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": GITHUB_REDIRECT_URI,
    }

    headers = {"Accept": "application/json"}

    async with httpx.AsyncClient() as client:
        token_response = await client.post(GITHUB_TOKEN_URL, data=token_data, headers=headers)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        access_token = tokens.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to obtain access token from GitHub.")
        
        userinfo_headers = {"Authorization": f"token {access_token}"}
        userinfo_response = await client.get(GITHUB_USERINFO_URL, headers=userinfo_headers)
        userinfo_response.raise_for_status()
        user_info = userinfo_response.json()

        # GitHub may not include email in /user; fetch from /user/emails if missing
        if not user_info.get("email"):
            emails_resp = await client.get("https://api.github.com/user/emails", headers=userinfo_headers)
            emails_resp.raise_for_status()
            emails = emails_resp.json()
            primary_email = next((e["email"] for e in emails if e.get("primary") and e.get("verified")), None)
            if not primary_email and emails:
                primary_email = emails[0].get("email")
            if primary_email:
                user_info["email"] = primary_email

        return user_info
      
def login_with_github(user_info: dict, db: dbSession, remember: bool = False) -> Token:
    email = user_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not available from GitHub profile.")

    user = db.query(userSchema).filter(userSchema.email == email).first()
    if not user:
        login_name = user_info.get("login") or email.split("@")[0]
        display_name = user_info.get("name") or ""
        # Try to split display name into first/last
        parts = display_name.split()
        username = parts[0] if parts else login_name
        lastname = " ".join(parts[1:]) if len(parts) > 1 else ""

        random_password = secrets.token_urlsafe(12)
        new_user = UserBase(
            username=username,
            lastname=lastname,
            email=email,
            password=random_password,
        )
        user = create_user(new_user, db)["data"]["user"]

    token_str = create_access_token(subject=user.email, user_id=user.id, remember=remember)
    return Token(access_token=token_str, token_type="bearer")