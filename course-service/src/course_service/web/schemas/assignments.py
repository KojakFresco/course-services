from datetime import date
from typing import Annotated
from uuid import UUID

from pydantic import AnyUrl, AwareDatetime, Field

from course_service.web.schemas.base_schemas import BaseSchemaModel, Pagination


class AssignmentCreate(BaseSchemaModel):
    title: Annotated[str, Field(examples=["Лабораторная работа №2 по REST API"])]
    description: Annotated[
        str,
        Field(examples=["Разработать и задокументировать контракты в формате OpenAPI"]),
    ]
    course_id: Annotated[UUID, Field(examples=["00000000-0000-0000-0000-000000000000"])]
    attempts_limit: Annotated[
        int,
        Field(
            description="Ограничение количества попыток сдачи (от 3 до 10)",
            examples=[3],
            ge=3,
            le=10,
        ),
    ]
    date_start: Annotated[
        date,
        Field(description="Дата начала выполнения задания", examples=["2026-10-01"]),
    ]
    date_end: Annotated[
        date, Field(description="Дедлайн сдачи задания", examples=["2026-10-20"])
    ]
    materials_url: Annotated[
        AnyUrl | None,
        Field(
            description="Ссылка на методические материалы",
            examples=["https://university.com/materials/lab2.pdf"],
        ),
    ] = None


class AssignmentUpdate(BaseSchemaModel):
    title: Annotated[
        str | None, Field(examples=["Лабораторная работа №2 (обновленная)"])
    ] = None
    description: Annotated[
        str | None, Field(examples=["Добавлены требования к покрытию тестами"])
    ] = None
    attempts_limit: Annotated[int | None, Field(examples=[5], ge=3, le=10)] = None
    date_start: Annotated[date | None, Field(examples=["2026-10-02"])] = None
    date_end: Annotated[date | None, Field(examples=["2026-10-25"])] = None
    materials_url: Annotated[
        AnyUrl | None,
        Field(examples=["https://university.com/materials/lab2_v2.pdf"]),
    ] = None


class Assignment(AssignmentCreate):
    id: Annotated[UUID, Field(examples=["55555555-5555-5555-5555-555555555555"])]
    created_at: Annotated[AwareDatetime, Field(examples=["2026-09-01T00:00:00Z"])]
    updated_at: Annotated[AwareDatetime, Field(examples=["2026-09-01T12:30:00Z"])]


class AssignmentsGetResponse(BaseSchemaModel):
    data: list[Assignment]
    pagination: Pagination
