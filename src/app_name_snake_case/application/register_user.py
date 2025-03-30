from dataclasses import dataclass

from effect import just

from app_name_snake_case.application.ports.map import (
    Map,
    NotUniqueUserNameError,
)
from app_name_snake_case.application.ports.transaction import Transaction
from app_name_snake_case.application.ports.user_id_signing import (
    UserIDSigning,
)
from app_name_snake_case.application.ports.user_views import UserViews
from app_name_snake_case.application.ports.users import Users
from app_name_snake_case.entities.core.user import (
    RegisteredUserForRegisteredUserError,
    registered_user_when,
)


@dataclass(kw_only=True, frozen=True, slots=True)
class Output[SignedUserIDT, UserViewT]:
    signed_user_id: SignedUserIDT
    user_view: UserViewT


@dataclass(kw_only=True, frozen=True, slots=True)
class RegisterUser[SignedUserIDT, UserViewT, UserViewWithIDT]:
    """
    :raises app_name_snake_case.entities.user.RegisteredUserForRegisteredUserError:
    """  # noqa: E501

    user_id_signing: UserIDSigning[SignedUserIDT]
    users: Users
    map: Map
    transaction: Transaction
    user_views: UserViews[UserViewT, UserViewWithIDT]

    async def __call__(
        self, signed_user_id: SignedUserIDT | None, user_name: str
    ) -> Output[SignedUserIDT, UserViewT]:
        if signed_user_id is None:
            user_id = None
        else:
            user_id = await self.user_id_signing.user_id_when(
                signed_user_id=signed_user_id
            )

        async with self.transaction:
            if user_id is None:
                user = None
            else:
                user = await self.users.user_with_id(user_id)

            registered_user = registered_user_when(
                user=user, user_name=user_name
            )

            try:
                await self.map(registered_user)
            except NotUniqueUserNameError as error:
                raise RegisteredUserForRegisteredUserError from error

            view = await self.user_views.view_of_user(just(registered_user))

        signed_user_id = await self.user_id_signing.signed_user_id_when(
            user_id=just(registered_user).id
        )
        return Output(signed_user_id=signed_user_id, user_view=view)
