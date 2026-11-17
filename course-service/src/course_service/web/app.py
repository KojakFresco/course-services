from collections.abc import Sequence
from typing import TypedDict, Unpack

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import Lifespan

from course_service.application.container import ApplicationContainer
from course_service.application.errors import (
    ApplicationNotConfiguredError,
    AssignmentNotFoundError,
    CourseNotFoundError,
    ReviewNotFoundError,
    SubmissionAttemptsLimitExceededError,
    SubmissionNotFoundError,
)
from course_service.core.config import Settings
from course_service.web.handlers import (
    application_error_handler,
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

    app.state.application = ApplicationContainer()
    app.state.storage_backend = settings.storage_backend
    app.state.max_page_size = settings.max_page_size

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
    for application_error in (
        CourseNotFoundError,
        AssignmentNotFoundError,
        SubmissionNotFoundError,
        ReviewNotFoundError,
        SubmissionAttemptsLimitExceededError,
        ApplicationNotConfiguredError,
    ):
        app.add_exception_handler(application_error, application_error_handler)

    app.middleware("http")(correlation_middleware)
    for router in routers:
        app.include_router(router)

    return app
