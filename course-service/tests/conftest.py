import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from course_service.core.config import Settings, get_settings
from course_service.web.api.v1 import api_router
from course_service.web.app import create_app


@pytest.fixture
def settings() -> Settings:
    return get_settings()


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    return create_app(settings, (api_router,))


@pytest.fixture
def app_client(app: FastAPI) -> TestClient:
    return TestClient(app)
