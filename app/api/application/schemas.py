from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BaseModelConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ApplicationSchema(BaseModelConfig):
    user_name: str = Field(max_length=20, description="имя пользователя")
    description: str = Field(description="описание заявки")

    @field_validator("user_name")
    def validate_user_name(cls, value):
        return value.lower()


class ApplicationCreateSchema(ApplicationSchema):
    pass


class ApplicationRespSchema(ApplicationSchema):
    id: int
    created_at: datetime

    @field_validator("created_at")
    def format_created_at(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%d-%m-%Y %H:%M:%S")
        return v


class ApplicationUpdateSchema(BaseModelConfig):
    user_name: str | None = Field(
        default=None,
        max_length=20,
        description="имя пользователя",
    )
    description: str | None = Field(default=None, max_length=100, description="описание заявки")


class ApplicationUpdateResponseSchema(BaseModel):
    message: str


class ApplicationFilterSchema(BaseModelConfig):
    id: int


class ApplicationsPagFilterSchema(BaseModel):
    user_name: str | None = Field(
        default=None,
        max_length=20,
        description="имя пользователя",
    )
