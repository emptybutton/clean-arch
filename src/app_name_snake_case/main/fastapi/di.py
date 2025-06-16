from dishka import Provider, Scope, make_async_container, provide

from app_name_snake_case import __version__
from app_name_snake_case.main.common.di import CommonProvider
from app_name_snake_case.presentation.fastapi.app import (
    FastAPIAppCoroutines,
    FastAPIAppRouters,
    FastAPIAppVersion,
)
from app_name_snake_case.presentation.fastapi.routers import all_routers


class FastAPIProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_routers(self) -> FastAPIAppRouters:
        return FastAPIAppRouters(all_routers)

    @provide(scope=Scope.APP)
    def provide_coroutines(self) -> FastAPIAppCoroutines:
        return FastAPIAppCoroutines(tuple())

    @provide(scope=Scope.APP)
    def provide_version(self) -> FastAPIAppVersion:
        return FastAPIAppVersion(__version__)


container = make_async_container(FastAPIProvider(), CommonProvider())
