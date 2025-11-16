from fastapi import Depends
from models import user_model
from database.postgresdb import dbSession
from sqlalchemy import select
from controller.auth_controller import create_access_token, get_password_hash, verify_password
from middlewares.exceptions import UserNotFoundError, InvalidPasswordError, PasswordMismatchError
import logging


async def get_users(db: dbSession):
    result = await db.execute(select(user_model.userSchema))
    return result.scalars().all()


async def get_user_by_id(user_id: int, db: dbSession):
    result = await db.execute(
        select(user_model.userSchema).where(user_model.userSchema.id == user_id)
    )
    db_user = result.scalar_one_or_none()
    if not db_user:
        logging.warning(f"User with ID {user_id} not found.")
        raise UserNotFoundError(user_id)
    logging.info(f"User with ID {user_id} retrieved successfully.")
    return db_user


async def create_user(user: user_model.UserBase, db: dbSession):
    hashed_password = get_password_hash(user.password)
    user.password = hashed_password
    db_user = user_model.userSchema(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return {
        "success": True,
        "data": {
            "user": db_user,
        },
    }


# def update_user(user_id: int, user: UserBase, db: dbSession):

async def change_password(user_id: int, password_update: user_model.PasswordUpdate, db: dbSession):
    try:
        user = await get_user_by_id(user_id, db)
        if not verify_password(password_update.current_password, user.password):
            logging.warning(f"Invalid current password for user ID {user_id}.")
            raise InvalidPasswordError()

        # Verify new password
        if password_update.new_password != password_update.new_password_confirm:
            logging.warning(f"Password mismatch for user ID {user_id}.")
            raise PasswordMismatchError()

        # Update password
        user.password = get_password_hash(password_update.new_password)
        await db.commit()
        logging.info(f"Password updated successfully for user ID {user_id}.")
    except Exception as e:
        logging.error(f"Error changing password for user ID {user_id}: {e}")
        raise e
    

async def delete_user(user_id: int, db: dbSession):
    result = await db.execute(
        select(user_model.userSchema).where(user_model.userSchema.id == user_id)
    )
    db_user = result.scalar_one_or_none()
    if db_user:
        await db.delete(db_user)
        await db.commit()
        return {"message": "User deleted successfully"}
    return {"message": "User not found"}