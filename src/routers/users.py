from datetime import datetime, timezone
from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.errors import DuplicateKeyError
from ulid import ulid

from src.database import Database
from src.schemas.base import MessageResponse
from src.schemas.users import (
    UserCreateInput,
    UserList,
    UserResponse,
    UserType,
    UserUpdateInput,
)
from src.security import get_password_hash, verify_password


async def get_collection(db: Database):
    collection: AsyncCollection[UserType] = db.get_collection("users")
    if "idx_username" not in await collection.index_information():
        await collection.create_index("username", name="idx_username", unique=True)

    return collection


Collection = Annotated[AsyncCollection[UserType], Depends(get_collection)]


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=UserList)
async def index_users(collection: Collection):
    list_users = await collection.find().to_list()
    return dict(data=list_users)


@router.get("/{user_id}", response_model=UserResponse)
async def show_user(user_id: str, collection: Collection):
    user = await collection.find_one({"_id": user_id})
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Usuário não encontrado",
        )

    return dict(data=user)


@router.post("/", response_model=MessageResponse)
async def create_user(user_data: UserCreateInput, collection: Collection):
    try:
        result = await collection.insert_one(
            {
                "_id": ulid(),
                "username": user_data.username,
                "password": get_password_hash(user_data.password),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    except DuplicateKeyError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail="Username não esta disponivel!"
        )

    if not result.acknowledged:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Erro na criação de usuário, tente novamente mais tarde",
        )

    return dict(message="Usuário criado!")


@router.put("/{user_id}", response_model=MessageResponse)
async def update_user(user_id: str, user_data: UserUpdateInput, collection: Collection):
    user = await collection.find_one({"_id": user_id})
    if user_data.password is not None and verify_password(
        user_data.password, user["password"]
    ):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="A nova senha não pode ser igual a senha atual!",
        )

    updated_data = user_data.model_dump(exclude_none=True, exclude_unset=True).copy()

    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Usuário não encontrado!"
        )

    is_updated = any(user.get(k) != v for k, v in updated_data.items())
    if is_updated:
        updated_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    else:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Nada a ser atualizado!"
        )

    if "password" in updated_data:
        updated_data["password"] = get_password_hash(updated_data["password"])

    try:
        result = await collection.update_one(
            {"_id": user_id},
            {"$set": updated_data},
        )
    except DuplicateKeyError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail="Username não esta disponivel!"
        )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Erro ao atualizar tentar atualizar o usuário, tente novamente mais tarde!",
        )

    return dict(message="Usuário atualizado!")


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete(user_id: str, collection: Collection):
    result = await collection.delete_one({"_id": user_id})

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Usuário não encontrado!",
        )

    return dict(message="Usuário deletado!")
