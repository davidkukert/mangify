from datetime import datetime, timezone
from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from pymongo.errors import DuplicateKeyError
from ulid import ulid

from src.database import MangaCollection
from src.schemas.base import MessageResponse
from src.schemas.mangas import (
    MangaCreateInput,
    MangaList,
    MangaResponse,
    MangaType,
    MangaUpdateInput,
)

router = APIRouter(prefix='/mangas', tags=['Mangas'])


@router.get('/', response_model=MangaList)
async def index_mangas(collection: MangaCollection):
    list_mangas = await collection.find().to_list()
    return dict(data=list_mangas)


@router.get('/{manga_id}', response_model=MangaResponse)
async def show_manga(manga_id: str, collection: MangaCollection):
    manga = await collection.find_one({'_id': manga_id})
    if manga is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Manga não encontrado'
        )
    return dict(data=manga)


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=MessageResponse
)
async def create_manga(
    collection: MangaCollection, manga_data: MangaCreateInput
):
    try:
        await collection.insert_one(
            MangaType(
                _id=ulid(),
                title=manga_data.title,
                alternatives_titles=manga_data.alternatives_titles,
                description=manga_data.description,
                original_language=manga_data.original_language,
                publication_demographic=manga_data.publication_demographic,
                status=manga_data.status,
                year=manga_data.year,
                content_rating=manga_data.content_rating,
                state=manga_data.state,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        )
    except DuplicateKeyError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Manga com esse título já existe!',
        )

    return dict(message='Manga criado')


@router.put('/{manga_id}', response_model=MessageResponse)
async def update_manga(
    manga_id: str, collection: MangaCollection, manga_data: MangaUpdateInput
):
    manga = await collection.find_one({'_id': manga_id})
    if manga is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Manga não encontrado'
        )
    updated_data = manga_data.model_dump(
        exclude_none=True, exclude_unset=True
    ).copy()

    is_updated = any(manga.get(k) != v for k, v in updated_data.items())
    if is_updated:
        updated_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    else:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Nada a ser atualizado!'
        )

    try:
        await collection.update_one(
            {'_id': manga_id},
            {'$set': updated_data},
        )
    except DuplicateKeyError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Manga com esse título já existe!',
        )

    return dict(message='Manga atualizado')


@router.delete('/{manga_id}', response_model=MessageResponse)
async def delete_manga(manga_id: str, collection: MangaCollection):
    result = await collection.delete_one({'_id': manga_id})

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Manga não encontrado!',
        )

    return dict(message='Manga deletado')
