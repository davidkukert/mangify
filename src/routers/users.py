from datetime import datetime, timezone
from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from pymongo.errors import DuplicateKeyError
from ulid import ulid

from src.auth.authorization import get_authorization
from src.database import UserCollection
from src.schemas.base import MessageResponse
from src.schemas.users import (
    RoleEnum,
    UserCreateInput,
    UserDB,
    UserList,
    UserResponse,
    UserType,
    UserUpdateInput,
)
from src.security import CurrentUser, get_password_hash, verify_password

router = APIRouter(prefix='/users', tags=['Users'])


@router.get('/', response_model=UserList)
async def index_users(collection: UserCollection):
    list_users = await collection.find().to_list()
    return dict(data=list_users)


@router.get('/{user_id}', response_model=UserResponse)
async def show_user(user_id: str, collection: UserCollection):
    user = await collection.find_one({'_id': user_id})
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Usuário não encontrado',
        )

    return dict(data=user)


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=MessageResponse
)
async def create_user(user_data: UserCreateInput, collection: UserCollection):
    try:
        await collection.insert_one(
            UserType(
                _id=ulid(),
                username=user_data.username,
                password=get_password_hash(user_data.password),
                role=RoleEnum.READER,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        )
    except DuplicateKeyError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username não esta disponível!',
        )

    return dict(message='Usuário criado!')


@router.put('/{user_id}', response_model=MessageResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdateInput,
    collection: UserCollection,
    current_user: CurrentUser,
):
    user = await collection.find_one({'_id': user_id})

    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Usuário não encontrado!'
        )

    await get_authorization(
        current_user, UserDB.model_validate(user), 'update', 'user'
    )

    if user_data.password is not None and verify_password(
        user_data.password, user['password']
    ):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='A nova senha não pode ser igual a senha atual!',
        )

    updated_data = user_data.model_dump(
        exclude_none=True, exclude_unset=True
    ).copy()

    is_updated = any(user.get(k) != v for k, v in updated_data.items())
    if is_updated:
        updated_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    else:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Nada a ser atualizado!'
        )

    updated_data['password'] = (
        get_password_hash(updated_data['password'])
        if 'password' in updated_data
        else user['password']
    )

    try:
        await collection.update_one(
            {'_id': user_id},
            {'$set': updated_data},
        )
    except DuplicateKeyError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username não esta disponível!',
        )

    return dict(message='Usuário atualizado!')


@router.delete('/{user_id}', response_model=MessageResponse)
async def delete(
    user_id: str, collection: UserCollection, current_user: CurrentUser
):
    user = await collection.find_one({'_id': user_id})
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Usuário não encontrado!',
        )

    await get_authorization(
        current_user, UserDB.model_validate(user), 'delete', 'user'
    )

    await collection.delete_one({'_id': user_id})

    return dict(message='Usuário deletado!')
