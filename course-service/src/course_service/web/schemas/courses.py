from enum import Enum
from typing import Annotated
from uuid import UUID

from pydantic import AwareDatetime, Field

from course_service.web.schemas.base_schemas import BaseSchemaModel, Pagination


class CourseStatus(Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    DRAFT = "DRAFT"


class CourseCreate(BaseSchemaModel):
    title: Annotated[
        str,
        Field(examples=["Backend-разработка на Python"], max_length=255, min_length=15),
    ]
    description: Annotated[
        str,
        Field(
            examples=[
                "Полный курс по разработке серверных приложений и проектированию REST API."
            ],
            max_length=4056,
            min_length=32,
        ),
    ]
    teacher_id: Annotated[
        UUID,
        Field(
            description="Идентификатор назначенного преподавателя (1 курс = 1 преподаватель)",
            examples=["11111111-1111-1111-1111-111111111111"],
        ),
    ]
    status: Annotated[CourseStatus, Field(examples=["ACTIVE"])]


class CourseUpdate(BaseSchemaModel):
    title: Annotated[
        str | None,
        Field(
            examples=["Продвинутый Backend на Python"], max_length=255, min_length=15
        ),
    ] = None
    description: Annotated[
        str | None,
        Field(
            examples=[
                "Углубленный курс по асинхронному программированию и оптимизации БД."
            ],
            max_length=4056,
            min_length=32,
        ),
    ] = None
    teacher_id: Annotated[
        UUID | None, Field(examples=["22222222-2222-2222-2222-222222222222"])
    ] = None
    status: Annotated[CourseStatus | None, Field(examples=["CLOSED"])] = None


class Course(CourseCreate):
    id: Annotated[UUID, Field(examples=["00000000-0000-0000-0000-000000000000"])]
    created_at: Annotated[AwareDatetime, Field(examples=["2026-09-01T00:00:00Z"])]
    updated_at: Annotated[AwareDatetime, Field(examples=["2026-09-05T14:30:00Z"])]


class CoursesGetResponse(BaseSchemaModel):
    data: list[Course]
    pagination: Pagination
