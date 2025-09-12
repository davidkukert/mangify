from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
    )


class ModelSchema(BaseSchema):
    id: str = Field(validation_alias=AliasChoices('id', '_id'))


class MessageResponse(BaseSchema):
    message: str


class TokenSchema(BaseSchema):
    access_token: str
    token_type: str
