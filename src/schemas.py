from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field



class ContactBase(BaseModel):
    name: str = Field(max_length=50)
    surname: str = Field(max_length=150)
    mobile: str = Field(max_length=50)
    email: str = Field(max_length=150)
    birthday: datetime = Field()

class ContactResponse(ContactBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"