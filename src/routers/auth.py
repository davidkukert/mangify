from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.database import UserCollection
from src.schemas.base import TokenSchema
from src.schemas.users import UserResponse
from src.security import CurrentUser, create_access_token, verify_password

router = APIRouter(prefix='/auth', tags=['Auth'])

OAuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token', response_model=TokenSchema)
async def login_for_access_token(
    form_data: OAuthForm, collection: UserCollection
):
    user = await collection.find_one({'username': form_data.username})

    if user is None or not verify_password(
        form_data.password, user['password']
    ):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Nome de usuário ou senha incorretos',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    access_token = create_access_token(dict(sub=user['_id']))
    return dict(access_token=access_token, token_type='bearer')


@router.post('/refresh', response_model=TokenSchema)
async def refresh_access_token(user: CurrentUser):
    new_access_token = create_access_token(dict(sub=user['_id']))
    return dict(access_token=new_access_token, token_type='bearer')


@router.get('/me', response_model=UserResponse)
async def get_me(user: CurrentUser):
    return dict(data=user)
