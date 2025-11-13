from fastapi import Depends
from models import user_model
from database.postgresdb import get_db
from sqlalchemy.orm import Session
from controller.auth_controller import create_access_token, get_password_hash, verify_password
from middlewares.exceptions import UserNotFoundError, InvalidPasswordError, PasswordMismatchError
import logging



def get_users(db: Session = Depends(get_db)):
    db_users = db.query(user_model.userSchema).all()
    return db_users


def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(user_model.userSchema).filter(user_model.userSchema.id == user_id).first()
    if not db_user:
      logging.warning(f"User with ID {user_id} not found.")
      raise UserNotFoundError(user_id)
    logging.info(f"User with ID {user_id} retrieved successfully.")
    return db_user


def create_user(user: user_model.UserBase, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    user.password = hashed_password
    db_user = user_model.userSchema(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return { 
            "success": True,
            "data": {
                "user": db_user,
            }
        }


# def update_user(user_id: int, user: UserBase, db: Session = Depends(get_db)):

def change_password(user_id: int, password_update: user_model.PasswordUpdate, db: Session = Depends(get_db)):
  try:
    user = get_user_by_id(user_id, db)
    if not verify_password(password_update.current_password, user.password):
        logging.warning(f"Invalid current password for user ID {user_id}.")
        raise InvalidPasswordError()

    # Verify new password
    if password_update.new_password != password_update.new_password_confirm:
        logging.warning(f"Password mismatch for user ID {user_id}.")
        raise PasswordMismatchError()
    
    # Update password
    user.password = get_password_hash(password_update.new_password)
    db.commit()
    logging.info(f"Password updated successfully for user ID {user_id}.")
  except Exception as e:
    logging.error(f"Error changing password for user ID {user_id}: {e}")
    raise e
    

def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(user_model.userSchema).filter(user_model.userSchema.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return {"message": "User deleted successfully"}
    return {"message": "User not found"}