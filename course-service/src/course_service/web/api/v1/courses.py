from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query

from course_service.application.services import CourseService
from course_service.web.dependencies import (
    get_course_service,
)
from course_service.web.schemas.base_schemas import Pagination
from course_service.web.schemas.courses import (
    Course,
    CourseCreate,
    CoursesGetResponse,
    CourseUpdate,
)
from course_service.web.schemas.errors import ErrorResponse

courses_router = APIRouter(prefix="/api/v1/courses", tags=["Courses"])


@courses_router.get(
    "/", response_model=CoursesGetResponse, responses={"401": {"model": ErrorResponse}}
)
async def list_courses(
    service: Annotated[CourseService, Depends(get_course_service)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> CoursesGetResponse:
    page = await service.list(offset=offset, limit=limit)
    return CoursesGetResponse(
        data=page.items,
        pagination=Pagination(offset=page.offset, limit=page.limit, total=page.total),
    )


@courses_router.post(
    "/",
    response_model=Course,
    status_code=201,
    responses={
        "400": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
    },
)
async def create_course(
    body: CourseCreate,
    idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")],
    service: Annotated[CourseService, Depends(get_course_service)],
) -> Course:
    return await service.create(body, idempotency_key)


@courses_router.get(
    "/{id}",
    response_model=Course,
    responses={"401": {"model": ErrorResponse}, "404": {"model": ErrorResponse}},
)
async def get_course(
    id: UUID,
    service: Annotated[CourseService, Depends(get_course_service)],
) -> Course:
    return await service.get(id)


@courses_router.patch(
    "/{id}",
    response_model=Course,
    responses={
        "400": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
        "404": {"model": ErrorResponse},
    },
)
async def update_course(
    id: UUID,
    body: CourseUpdate,
    service: Annotated[CourseService, Depends(get_course_service)],
) -> Course:
    return await service.update(id, body)


@courses_router.delete(
    "/{id}",
    status_code=204,
    responses={
        "401": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
        "404": {"model": ErrorResponse},
    },
)
async def delete_course(
    id: UUID,
    service: Annotated[CourseService, Depends(get_course_service)],
) -> None:
    await service.delete(id)
