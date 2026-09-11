from pydantic import BaseModel, EmailStr

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