from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from app_name_snake_case.presentation.fastapi.schemas.common import ErrorSchema


class UserSchema(BaseModel):
    id: UUID
    name: str


class AlreadyRegisteredUserSchema(ErrorSchema):
    type: Literal["alreadyRegisteredUser"] = "alreadyRegisteredUser"
