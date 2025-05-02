from typing import Literal

from pydantic import BaseModel


class UserSchema(BaseModel):
    name: str


class AlreadyRegisteredUserSchema(BaseModel):
    type: Literal["alreadyRegisteredUser"] = "alreadyRegisteredUser"


class AlreadyTakenUserNameSchema(BaseModel):
    type: Literal["alreadyTakenUserName"] = "alreadyTakenUserName"
