from datetime import datetime, timezone
from http import HTTPStatus

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from ulid import ulid

from src.app import app
from src.database import DBClient, get_db, get_db_client, get_user_collection
from src.schemas.users import UserType
from src.security import get_password_hash

DB_TEST_NAME = 'test_mangify'


@pytest.fixture
def db_client():
    client = get_db_client()
    return client.get_database(DB_TEST_NAME)


@pytest.fixture
def client():
    async def get_db_test(client: DBClient):
        yield client.get_database(DB_TEST_NAME)

    with TestClient(app) as c:
        app.dependency_overrides[get_db] = get_db_test
        yield c


@pytest_asyncio.fixture
async def user(db_client) -> UserType:
    collection = await get_user_collection(db_client)
    result = await collection.insert_one(
        UserType(
            _id=ulid(),
            username='testuser',
            password=get_password_hash('testpassword'),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    user = await collection.find_one({'_id': result.inserted_id})
    if user is None:
        pytest.fail('Failed to create test user')
    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user['username'], 'password': 'testpassword'},
    )
    if response.status_code != HTTPStatus.OK:
        pytest.fail('Failed to obtain access token')
    return response.json()['accessToken']


@pytest_asyncio.fixture(autouse=True)
async def clear_database():
    client = get_db_client()
    await client.drop_database(DB_TEST_NAME)
