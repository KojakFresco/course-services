from collections.abc import Sequence
from typing import TypedDict, Unpack

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import Lifespan

from course_service.core.config import Settings
from course_service.repositories.container import RepositoryContainer
from course_service.web.handlers import (
    http_exception_handler,
    unexpected_exception_handler,
    validation_exception_handler,
)
from course_service.web.middlewares import correlation_middleware


class FastAPIParams(TypedDict, total=False):
    title: str
    description: str
    version: str
    debug: bool
    lifespan: Lifespan[FastAPI]


def create_app(
    settings: Settings, routers: Sequence[APIRouter], **params: Unpack[FastAPIParams]
) -> FastAPI:
    app_params = {**settings.app.model_dump(), **params}
    app = FastAPI(**app_params)

    app.state.repositories = RepositoryContainer()

    app.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler,
    )
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )
    app.add_exception_handler(
        Exception,
        unexpected_exception_handler,
    )

    app.middleware("http")(correlation_middleware)
    for router in routers:
        app.include_router(router)

    return app
