from fastapi import APIRouter, status
from database.postgresdb import dbSession
from controller import user_controller, auth_controller
from models import user_model, auth_model


user_router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@user_router.get("/")
async def get_users(db: dbSession):
    db_users = user_controller.get_users(db)
    return {"users": db_users}


@user_router.get("/me", response_model=user_model.UserBase)
def get_current_user(current_user: auth_controller.CurrentUser, db: dbSession):
    db_user = user_controller.get_user_by_id(current_user.user_id, db)
    return db_user


@user_router.put("/change-password", status_code=status.HTTP_200_OK)
async def change_password(current_user: auth_controller.CurrentUser, password_update: user_model.PasswordUpdate, db: dbSession):
    return user_controller.change_password(current_user.user_id, password_update, db)

@user_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(current_user: auth_controller.CurrentUser, db: dbSession):
    return user_controller.delete_user(current_user.user_id, db)
    
