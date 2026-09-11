from pydantic import BaseModel, EmailStr

class UserUpdateRequest(BaseModel):
    name : str | None = None
    email : EmailStr | None = None

class RegisterRequest(BaseModel):
    name : str
    email : EmailStr
    password : str
