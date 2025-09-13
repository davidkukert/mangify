from datetime import datetime
from enum import Enum
from typing import TypedDict

from pydantic import Field

from src.schemas.base import BaseSchema, ModelSchema


class RoleEnum(str, Enum):
    ADMIN = 'admin'
    READER = 'reader'


class UserCreateInput(BaseSchema):
    username: str
    password: str


class UserUpdateInput(BaseSchema):
    username: str | None = None
    password: str | None = None


class UserSchema(ModelSchema):
    username: str
    role: RoleEnum = Field(default=RoleEnum.READER)
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
    role: RoleEnum
    created_at: datetime
    updated_at: datetime


class UserDB(ModelSchema):
    username: str
    password: str
    role: RoleEnum = Field(default=RoleEnum.READER)
    created_at: datetime
    updated_at: datetime
