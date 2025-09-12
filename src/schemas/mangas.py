from datetime import datetime
from enum import Enum
from typing import TypedDict

from pydantic import Field

from src.schemas.base import BaseSchema, ModelSchema


class StatusEnum(str, Enum):
    ONGOING = 'ongoing'
    COMPLETED = 'completed'
    HIATUS = 'hiatus'
    CANCELLED = 'cancelled'


class ContentRatingEnum(str, Enum):
    SAFE = 'safe'
    SUGGESTIVE = 'suggestive'
    EROTICA = 'erotica'
    PORNOGRAPHIC = 'pornographic'


class StateEnum(str, Enum):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    SUBMITTED = 'submitted'
    REJECTED = 'rejected'


class DemographicEnum(str, Enum):
    SHONEN = 'shonen'
    SHOJO = 'shojo'
    SEINEN = 'seinen'
    JOSEI = 'josei'


class MangaType(TypedDict):
    _id: str
    title: str
    alternatives_titles: list[str]
    description: str | None
    original_language: str
    publication_demographic: DemographicEnum | None
    status: StatusEnum
    year: int | None
    content_rating: ContentRatingEnum
    state: StateEnum
    created_at: datetime
    updated_at: datetime


class MangaCreateInput(BaseSchema):
    title: str
    alternatives_titles: list[str] = Field(default_factory=list)
    description: str | None = Field(default=None)
    original_language: str = Field(pattern=r'^[a-z]{2}$')
    publication_demographic: DemographicEnum | None = Field(default=None)
    status: StatusEnum
    year: int | None = Field(default=None, ge=1900)
    content_rating: ContentRatingEnum
    state: StateEnum = Field(default=StateEnum.DRAFT)


class MangaUpdateInput(BaseSchema):
    title: str | None = Field(default=None)
    alternatives_titles: list[str] | None = Field(default=None)
    description: str | None = Field(default=None)
    original_language: str | None = Field(default=None, pattern=r'^[a-z]{2}$')
    publication_demographic: DemographicEnum | None = Field(default=None)
    status: StatusEnum | None = Field(default=None)
    year: int | None = Field(default=None, ge=1900)
    content_rating: ContentRatingEnum | None = Field(default=None)
    state: StateEnum | None = Field(default=None)


class MangaSchema(ModelSchema):
    title: str
    alternatives_titles: list[str]
    description: str | None = None
    original_language: str
    publication_demographic: DemographicEnum | None = None
    status: StatusEnum
    year: int | None = None
    content_rating: ContentRatingEnum
    state: StateEnum
    created_at: datetime
    updated_at: datetime


class MangaResponse(BaseSchema):
    data: MangaSchema


class MangaList(BaseSchema):
    data: list[MangaSchema]
