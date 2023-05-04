from pydantic import BaseModel

class Token(BaseModel):
    access_token: str

# Base class is schema for request body
class UserBase(BaseModel):
    email: str
    full_name: str
    password: str

# Schema class is schema for response body and db object
class UserSchema(UserBase):
    id: int

    # allows conversion between Pydantic and ORMs
    class Config:
        orm_mode = True

class UsernameSchema(UserBase):
    username: str
