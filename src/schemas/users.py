from typing import TypedDict
from pydantic import Field
from src.schemas.base import BaseSchema
from datetime import datetime


class UserCreateInput(BaseSchema):
    username: str
    password: str


class UserUpdateInput(BaseSchema):
    username: str | None = None
    password: str | None = None


class UserSchema(BaseSchema):
    id: str = Field(validation_alias="_id")
    username: str
    created_at: datetime
    updated_at: datetime


class UserResponse(BaseSchema):
    data: UserSchema


class UserList(BaseSchema):
    data: list[UserSchema]


class UserType(TypedDict):
    _id: str
    username: str
    password: str
    created_at: datetime
    updated_at: datetime
