from fastapi import APIRouter

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@auth_router.post("/login")
async def login():
    return {"message": "Login endpoint"}

@auth_router.post("/register")
async def register():
    return {"message": "Register endpoint"}

@auth_router.post("/logout")
async def logout():
    return {"message": "Logout endpoint"}

