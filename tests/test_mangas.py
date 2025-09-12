from datetime import datetime, timezone
from http import HTTPStatus

import pytest
import pytest_asyncio
from ulid import ulid

from src.database import get_manga_collection
from src.schemas.mangas import (
    ContentRatingEnum,
    DemographicEnum,
    MangaCreateInput,
    MangaType,
    MangaUpdateInput,
    StateEnum,
    StatusEnum,
)


@pytest.fixture
def manga_data():
    return MangaCreateInput(
        title='Test Manga',
        alternatives_titles=['TM', 'TestM'],
        description='A test manga description.',
        original_language='ja',
        publication_demographic=DemographicEnum.SHONEN,
        status=StatusEnum.ONGOING,
        year=2023,
        content_rating=ContentRatingEnum.SAFE,
    )


@pytest_asyncio.fixture
async def manga(db_client) -> MangaType:
    collection = await get_manga_collection(db_client)
    result = await collection.insert_one(
        MangaType(
            _id=ulid(),
            title='Existing Manga',
            alternatives_titles=['EM', 'ExistM'],
            description='An existing manga description.',
            original_language='ja',
            publication_demographic=DemographicEnum.SHONEN,
            status=StatusEnum.ONGOING,
            year=2022,
            content_rating=ContentRatingEnum.SAFE,
            state=StateEnum.DRAFT,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    manga = await collection.find_one({'_id': result.inserted_id})
    if manga is None:
        pytest.fail('Failed to create test manga')
    return manga


@pytest_asyncio.fixture
async def manga_other(db_client) -> MangaType:
    collection = await get_manga_collection(db_client)
    result = await collection.insert_one(
        MangaType(
            _id=ulid(),
            title='Existing Other Manga',
            alternatives_titles=['EM', 'ExistM'],
            description='An existing manga description.',
            original_language='ja',
            publication_demographic=DemographicEnum.SHONEN,
            status=StatusEnum.ONGOING,
            year=2022,
            content_rating=ContentRatingEnum.SAFE,
            state=StateEnum.DRAFT,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    manga = await collection.find_one({'_id': result.inserted_id})
    if manga is None:
        pytest.fail('Failed to create test manga')
    return manga


def test_index_mangas(client):
    response = client.get('/mangas/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'data': []}


def test_create_manga(client, manga_data):
    response = client.post('/mangas/', json=manga_data.model_dump())
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'message': 'Manga criado'}


def test_create_existing_manga(client, manga: MangaType):
    response = client.post(
        '/mangas/',
        json=MangaCreateInput(
            title=manga['title'],
            alternatives_titles=manga['alternatives_titles'],
            description=manga['description'],
            original_language=manga['original_language'],
            publication_demographic=manga['publication_demographic'],
            status=manga['status'],
            year=manga['year'],
            content_rating=manga['content_rating'],
        ).model_dump(),
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Manga com esse título já existe!'}


def test_show_manga(client, manga: MangaType):
    response = client.get(f'/mangas/{manga["_id"]}')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'data': {
            'id': manga['_id'],
            'title': manga['title'],
            'alternativesTitles': manga['alternatives_titles'],
            'description': manga['description'],
            'originalLanguage': manga['original_language'],
            'publicationDemographic': (
                manga['publication_demographic']
                if manga['publication_demographic'] is not None
                else None
            ),
            'status': manga['status'],
            'year': manga['year'],
            'contentRating': manga['content_rating'],
            'state': manga['state'],
            'createdAt': manga['created_at'].isoformat(),
            'updatedAt': manga['updated_at'].isoformat(),
        }
    }


def test_show_nonexistent_manga(client):
    response = client.get(f'/mangas/{ulid()}')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Manga não encontrado'}


def test_update_manga(client, manga: MangaType):
    new_title = 'Updated Manga Title'
    response_update = client.put(
        f'/mangas/{manga["_id"]}',
        json=MangaCreateInput(
            title=new_title,
            alternatives_titles=manga['alternatives_titles'],
            description=manga['description'],
            original_language=manga['original_language'],
            publication_demographic=manga['publication_demographic'],
            status=manga['status'],
            year=manga['year'],
            content_rating=manga['content_rating'],
        ).model_dump(),
    )
    assert response_update.status_code == HTTPStatus.OK
    assert response_update.json() == {'message': 'Manga atualizado'}

    response = client.get(f'/mangas/{manga["_id"]}')
    assert response.status_code == HTTPStatus.OK
    assert response.json()['data']['title'] == new_title


def test_update_nonexistent_manga(client):
    response = client.put(
        f'/mangas/{ulid()}',
        json=dict(title='Nonexistent Manga'),
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Manga não encontrado'}


def test_delete_manga(client, manga: MangaType):
    response_delete = client.delete(f'/mangas/{manga["_id"]}')
    assert response_delete.status_code == HTTPStatus.OK
    assert response_delete.json() == {'message': 'Manga deletado'}

    response = client.get(f'/mangas/{manga["_id"]}')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Manga não encontrado'}


def test_delete_nonexistent_manga(client):
    response = client.delete(f'/mangas/{ulid()}')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Manga não encontrado!'}


def test_index_mangas_with_existing(client, manga: MangaType):
    response = client.get('/mangas/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'data': [
            {
                'id': manga['_id'],
                'title': manga['title'],
                'alternativesTitles': manga['alternatives_titles'],
                'description': manga['description'],
                'originalLanguage': manga['original_language'],
                'publicationDemographic': (
                    manga['publication_demographic']
                    if manga['publication_demographic'] is not None
                    else None
                ),
                'status': manga['status'],
                'year': manga['year'],
                'contentRating': manga['content_rating'],
                'state': manga['state'],
                'createdAt': manga['created_at'].isoformat(),
                'updatedAt': manga['updated_at'].isoformat(),
            }
        ]
    }


def test_create_manga_invalid_language(client, manga_data):
    manga_data.original_language = 'japan'
    response = client.post('/mangas/', json=manga_data.model_dump())
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_update_manga_to_existing_title(
    client, manga: MangaType, manga_other: MangaType
):
    response = client.put(
        f'/mangas/{manga["_id"]}',
        json=dict(title=manga_other['title']),
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Manga com esse título já existe!'}


def test_nothing_to_update_manga(client, manga: MangaType):
    response_update = client.put(
        f'/mangas/{manga["_id"]}',
        json=MangaUpdateInput(title=manga['title']).model_dump(
            exclude_none=True
        ),
    )
    assert response_update.status_code == HTTPStatus.BAD_REQUEST
    assert response_update.json() == {'detail': 'Nada a ser atualizado!'}
