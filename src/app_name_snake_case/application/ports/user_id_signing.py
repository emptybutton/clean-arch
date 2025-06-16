from abc import ABC, abstractmethod
from uuid import UUID


class UserIDSigning[SignedUserIDT](ABC):
    @abstractmethod
    async def signed_user_id(self, user_id: UUID, /) -> SignedUserIDT:
        ...

    @abstractmethod
    async def user_id(
        self, signed_user_id: SignedUserIDT, /,
    ) -> UUID | None: ...
