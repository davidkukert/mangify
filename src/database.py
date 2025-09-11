from typing import Annotated

from fastapi import Depends
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncCollection, AsyncDatabase

from src.schemas.users import UserType
from src.settings import settings


def get_db_client():
    return AsyncMongoClient(settings.DATABASE_URL)


DBClient = Annotated[AsyncMongoClient, Depends(get_db_client)]


def get_db(client: DBClient):
    return client.get_database(settings.DATABASE_NAME)


Database = Annotated[AsyncDatabase, Depends(get_db)]


async def get_user_collection(db: Database):
    collection: AsyncCollection[UserType] = db.get_collection('users')
    if 'idx_username' not in await collection.index_information():
        await collection.create_index(
            'username', name='idx_username', unique=True
        )

    return collection


UserCollection = Annotated[
    AsyncCollection[UserType], Depends(get_user_collection)
]
