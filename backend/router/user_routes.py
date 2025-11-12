from fastapi import APIRouter

user_router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@user_router.get("/")
async def get_users():
    return {"message": "Get all users endpoint"}

@user_router.get("/{user_id}")
async def get_user(user_id: int):
    return {"message": f"Get user with ID {user_id} endpoint"}

@user_router.post("/")
async def create_user():
    return {"message": "Create user endpoint"}

@user_router.put("/{user_id}")
async def update_user(user_id: int):
    return {"message": f"Update user with ID {user_id} endpoint"}

@user_router.delete("/{user_id}")
async def delete_user(user_id: int):
    return {"message": f"Delete user with ID {user_id} endpoint"}