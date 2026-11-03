from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from course_service.repositories import CourseRepository
from course_service.services.courses import CourseService
from course_service.web.dependencies import (
    get_course_repository,
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
    repository: Annotated[CourseRepository, Depends(get_course_repository)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> CoursesGetResponse:
    page = await repository.list(offset=offset, limit=limit)
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
    repository: Annotated[CourseRepository, Depends(get_course_repository)],
) -> Course:
    course = await repository.get(id)
    if course is None:
        raise HTTPException(404, "Course not found")
    return course


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
    repository: Annotated[CourseRepository, Depends(get_course_repository)],
) -> Course:
    course = await repository.get(id)
    if course is None:
        raise HTTPException(404, "Course not found")
    updated = course.model_copy(update=body.model_dump(exclude_unset=True), deep=True)
    updated.updated_at = datetime.now(UTC)
    return await repository.update(updated)


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
    repository: Annotated[CourseRepository, Depends(get_course_repository)],
) -> None:
    if not await repository.delete(id):
        raise HTTPException(404, "Course not found")
