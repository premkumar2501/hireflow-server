from pydantic import BaseModel
from app.schema.user import UserResponse

class RegisterResponse(BaseModel):
    user: UserResponse
    verification_token: str

class LoginRequest(BaseModel):
    email: str
    password: str
    
class VerifyUser(BaseModel):
    id: int
    token: str
