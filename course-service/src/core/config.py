import functools
from typing import final

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    title: str = "Course service title"
    description: str = "Course service description"
    summary: str = "Course service summary"
    # TODO: ...


@final
class Settings(BaseSettings):
    app: AppSettings

    model_config = SettingsConfigDict(
        extra="allow", env_file=".env",
        env_nested_delimiter="__", env_file_encoding="utf-8",
    )


@functools.lru_cache
def get_settings() -> Settings:
    return Settings(app=AppSettings())
