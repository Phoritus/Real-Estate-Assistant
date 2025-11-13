from fastapi import HTTPException

class UserError(HTTPException):
    pass
  
class UserNotFoundError(UserError):
    def __init__(self, user_id: int):
        message = "User not found" if user_id is None else f"User with ID {user_id} not found"
        super().__init__(status_code=404, detail=message)
  
class PasswordMismatchError(UserError):
    def __init__(self):
        super().__init__(status_code=400, detail="New password and confirmation do not match")

class InvalidPasswordError(UserError):
    def __init__(self):
        super().__init__(status_code=401, detail="Current password is incorrect")
        
class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=401, detail=detail)
        


class JWTValidationError(Exception):
    pass