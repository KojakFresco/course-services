from enum import Enum
from typing import Annotated
from uuid import UUID

from pydantic import AwareDatetime, Field

from course_service.web.schemas.base_schemas import BaseSchemaModel


class Type(Enum):
    auto = "auto"
    manual = "manual"


class ReviewStatus(Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"


class ReviewCreate(BaseSchemaModel):
    type: Annotated[Type, Field(description="Способ проверки", examples=["manual"])]
    feedback: Annotated[
        str,
        Field(examples=["Отличная архитектура, но не хватает обработки ошибок 409."]),
    ]
    mark: Annotated[float, Field(examples=[9.5], ge=0.0, le=10.0)]
    status: Annotated[ReviewStatus, Field(examples=["PASSED"])]


class ReviewUpdate(BaseSchemaModel):
    feedback: Annotated[
        str | None,
        Field(
            default=None,
            examples=["Исправлено: обработка 409 добавлена, оценка повышена."],
        ),
    ]
    mark: Annotated[float | None, Field(default=None, examples=[10.0], ge=0.0, le=10.0)]
    status: Annotated[ReviewStatus | None, Field(default=None, examples=["PASSED"])]


class Review(ReviewCreate):
    id: Annotated[UUID, Field(examples=["cccccccc-cccc-cccc-cccc-cccccccccccc"])]
    created_at: Annotated[AwareDatetime, Field(examples=["2026-10-16T10:00:00Z"])]
    updated_at: Annotated[AwareDatetime, Field(examples=["2026-10-16T10:15:00Z"])]
