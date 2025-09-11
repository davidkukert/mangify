from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from pwdlib import PasswordHash

from src.database import UserCollection
from src.schemas.users import UserType
from src.settings import settings

pwd_context = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='auth/token', refreshUrl='auth/refresh'
)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire})
    encoded_jwt = encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


async def get_current_user(
    collection: UserCollection, token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Não foi possível validar as credenciais',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        subject_id: str = payload.get('sub')
        if subject_id is None:
            raise credentials_exception
    except DecodeError:
        raise credentials_exception
    except ExpiredSignatureError:
        raise credentials_exception

    user = await collection.find_one({'_id': subject_id})

    if user is None:
        raise credentials_exception

    return user


CurrentUser = Annotated[UserType, Depends(get_current_user)]
