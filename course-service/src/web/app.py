from collections.abc import Sequence
from typing import TypedDict, Unpack

from fastapi import APIRouter, FastAPI
from starlette.types import Lifespan

from src.core.config import Settings


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
    for router in routers:
        app.include_router(router)
    return app
