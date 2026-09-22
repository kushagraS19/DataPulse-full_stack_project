from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    email : EmailStr
    password : str

class UserResponse(BaseModel):
    id : int
    name : str
    email : EmailStr

    model_config = {
        "from_attributes" : True
    }

class PasswordChangeVerifyRequest(BaseModel):
    otp: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8, max_length=128)

class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetVerifyRequest(BaseModel):
    email: EmailStr
    otp: str = Field(
        min_length=6,
        max_length=6
    )
    new_password: str = Field(
        min_length=8,
        max_length=128
    )

class EmailVerificationVerifyRequest(BaseModel):
    otp: str = Field(
        min_length=6,
        max_length=6
    )