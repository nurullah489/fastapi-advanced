from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: int
    active: bool = True

class UserUpdate(BaseModel):
    name: str
    email: EmailStr
    age: int
    active: bool

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int
    active: bool