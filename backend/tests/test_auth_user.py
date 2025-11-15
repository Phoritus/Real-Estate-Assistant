import os
import sys
import pathlib
import uuid
from fastapi.testclient import TestClient


# Ensure required env vars before importing app
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("JWT_SECRET_KEY", "testsecret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRATION_TIME", "60")  # minutes
os.environ.setdefault("DEV_PORT", "http://testclient")

# Ensure backend root is on sys.path for CI runners
BACKEND_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from main import app  # import FastAPI app directly when running in backend dir
client = TestClient(app)


def unique_user_payload(password: str = "TestPass123!"):
    return {
        "username": "user" + uuid.uuid4().hex[:6],
        "lastname": "ln" + uuid.uuid4().hex[:6],
        "email": f"test{uuid.uuid4().hex[:6]}@example.com",
        "password": password,
    }


def register_user(payload):
    resp = client.post("/auth/register", json=payload)
    return resp


def login_user(email: str, password: str):
    resp = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return resp


def test_register_and_login_flow():
    payload = unique_user_payload()
    # Register
    r = register_user(payload)
    assert r.status_code == 201, r.text
    # Login
    l = login_user(payload["email"], payload["password"])  # username field carries email
    assert l.status_code == 200, l.text
    data = l.json()
    assert "access_token" in data and data["token_type"] == "bearer"
    # Cookie should be set
    assert "access_token" in l.cookies


def test_users_me_unauthorized():
    r = client.get("/users/me")
    assert r.status_code == 401


def test_users_me_authorized():
    payload = unique_user_payload()
    reg = register_user(payload)
    assert reg.status_code == 201
    login = login_user(payload["email"], payload["password"])  # email used as username
    assert login.status_code == 200
    # Use cookie for authenticated request
    cookies = {"access_token": login.cookies.get("access_token")}
    me = client.get("/users/me", cookies=cookies)
    assert me.status_code == 200, me.text
    user = me.json()
    assert user["email"].lower() == payload["email"].lower()
    assert "password" not in user  # response_model excludes password


def test_change_password_and_login_new_password():
    payload = unique_user_payload("OldPass123!")
    reg = register_user(payload)
    assert reg.status_code == 201
    login = login_user(payload["email"], "OldPass123!")
    assert login.status_code == 200
    cookies = {"access_token": login.cookies.get("access_token")}

    # Change password
    change_payload = {
        "current_password": "OldPass123!",
        "new_password": "NewPass456!",
        "new_password_confirm": "NewPass456!",
    }
    ch = client.put("/users/change-password", json=change_payload, cookies=cookies)
    assert ch.status_code == 200, ch.text

    # Old password should fail
    old_login = login_user(payload["email"], "OldPass123!")
    assert old_login.status_code == 401

    # New password should work
    new_login = login_user(payload["email"], "NewPass456!")
    assert new_login.status_code == 200


def test_change_password_mismatch():
    payload = unique_user_payload("StartPass123!")
    reg = register_user(payload)
    assert reg.status_code == 201
    login = login_user(payload["email"], "StartPass123!")
    assert login.status_code == 200
    cookies = {"access_token": login.cookies.get("access_token")}
    # Mismatch new passwords
    change_payload = {
        "current_password": "StartPass123!",
        "new_password": "NewPass789!",
        "new_password_confirm": "DifferentPass!",
    }
    ch = client.put("/users/change-password", json=change_payload, cookies=cookies)
    assert ch.status_code == 400