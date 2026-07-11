from pydantic import BaseModel, EmailStr, Field

class UserRegisterSchema(BaseModel):
    """Schema for validating user registration requests."""
    username: str = Field(..., min_length=3, max_length=50, description="Unique account username")
    email: EmailStr = Field(..., description="Valid user email address")
    password: str = Field(..., min_length=8, max_length=128, description="Secured account password")
    role_id: int = Field(..., ge=1, description="Database role key index")

class UserLoginSchema(BaseModel):
    """Schema for validating login credential payloads."""
    username: str = Field(..., description="Account username")
    password: str = Field(..., description="Account password")

class TokenResponseSchema(BaseModel):
    """Schema validating JWT access tokens dispatch."""
    token: str
    expires_in: int
