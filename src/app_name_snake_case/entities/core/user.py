from dataclasses import dataclass
from typing import TypeGuard
from uuid import UUID, uuid4

from effect import IdentifiedValue, New, new


@dataclass(kw_only=True, frozen=True)
class User(IdentifiedValue[UUID]):
    name: str


type RegisteredUser = User
type UnregisteredUser = None
type AnyUser = RegisteredUser | UnregisteredUser


unregistered_user: UnregisteredUser = None


def is_registered(user: AnyUser) -> TypeGuard[RegisteredUser]:
    return user is not None


class RegisteredUserForRegisteredUserError(Exception): ...


def registered_user_when(*, user: AnyUser, user_name: str) -> New[User]:
    """
    :raises app_name_snake_case.entities.user.RegisteredUserForRegisteredUserError:
    """  # noqa: E501

    if is_registered(user):
        raise RegisteredUserForRegisteredUserError

    return new(User(id=uuid4(), name=user_name))
