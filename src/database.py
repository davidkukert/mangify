from typing import Annotated
from fastapi import Depends
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from src.settings import settings


def get_db_client():
    return AsyncMongoClient(settings.DATABASE_URL)


DBClient = Annotated[AsyncMongoClient, Depends(get_db_client)]


def get_db(client: DBClient):
    return client.get_database(settings.DATABASE_NAME)


Database = Annotated[AsyncDatabase, Depends(get_db)]
