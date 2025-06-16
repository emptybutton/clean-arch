import asyncio
from collections.abc import AsyncIterator, Callable, Coroutine
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from types import TracebackType
from typing import Any, NewType, Self, cast

from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import APIRouter, FastAPI
from fastapi.openapi.constants import REF_TEMPLATE
from pydantic import BaseModel

from app_name_snake_case.presentation.fastapi.tags import tags_metadata


FastAPIAppCoroutines = NewType(
    "FastAPIAppCoroutines",
    tuple[Callable[[], Coroutine[Any, Any, Any]], ...],
)
FastAPIAppRouters = NewType("FastAPIAppRouters", tuple[APIRouter, ...])
FastAPIAppVersion = NewType("FastAPIAppVersion", str)


@dataclass(frozen=True, unsafe_hash=False)
class AppBackgroundTasks:
    _loop: asyncio.AbstractEventLoop = field(
        default_factory=asyncio.get_running_loop,
    )
    _tasks: set[asyncio.Task[Any]] = field(init=False, default_factory=set)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        error_type: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        for task in self._tasks:
            task.cancel()

        await asyncio.gather(*self._tasks, return_exceptions=True)

    def create_task(
        self,
        func: Callable[[], Coroutine[Any, Any, Any]],
    ) -> None:
        decorated_func = self._decorator(func)
        self._create_task(decorated_func())

    def _decorator(
        self,
        func: Callable[[], Coroutine[Any, Any, Any]],
    ) -> Callable[[], Coroutine[Any, Any, Any]]:
        async def decorated_func() -> None:
            try:
                await func()
            except Exception as error:
                self._create_task(decorated_func())
                raise error from error

        return decorated_func

    def _create_task(self, coro: Coroutine[Any, Any, Any]) -> None:
        task = self._loop.create_task(coro)

        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with AppBackgroundTasks() as tasks:
        for coroutine in cast("FastAPIAppCoroutines", app.state.coroutines):
            tasks.create_task(coroutine)

        yield
        await app.state.dishka_container.close()


class _FastAPIWithAdditionalModels(FastAPI):
    __additional_model_types: tuple[type[BaseModel], ...] = tuple()

    def openapi(self) -> dict[str, Any]:
        if self.openapi_schema is not None:
            return self.openapi_schema

        schema = super().openapi()

        for model_type in self.__additional_model_types:
            schema["components"]["schemas"][model_type.__name__] = (
                model_type.model_json_schema(ref_template=REF_TEMPLATE)
            )

        return schema


async def app_from(container: AsyncContainer) -> FastAPI:
    author_url = "https://github.com/emptybutton"
    repo_url = f"{author_url}/app_name_kebab_case"
    version: FastAPIAppVersion = await container.get(FastAPIAppVersion)

    app = _FastAPIWithAdditionalModels(
        title="app-name-kebab-case",
        version=version,
        summary="app_name_description.",
        openapi_tags=tags_metadata,
        contact={"name": "Alexander Smolin", "url": author_url},
        license_info={
            "name": "Apache 2.0",
            "url": f"{repo_url}/blob/main/LICENSE",
        },
        lifespan=lifespan,
        root_path=f"/api/{version}",
    )

    app.state.coroutines = await container.get(FastAPIAppCoroutines)

    for router in await container.get(FastAPIAppRouters):
        app.include_router(router)

    setup_dishka(container=container, app=app)

    return app
