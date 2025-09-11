from pymongo.asynchronous.database import AsyncDatabase

from src.database import get_db, get_db_client


def test_get_database():
    client = get_db_client()
    db = get_db(client)
    assert db.name == 'mangify'
    assert isinstance(db, AsyncDatabase)
