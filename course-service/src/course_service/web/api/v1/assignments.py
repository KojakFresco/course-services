from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from course_service.repositories import AssignmentRepository, IdempotencyRepository
from course_service.repositories.container import RepositoryContainer
from course_service.web.dependencies import (
    get_assignment_repository,
    get_idempotency_repository,
    get_repositories,
)
from course_service.web.schemas.assignments import (
    Assignment,
    AssignmentCreate,
    AssignmentsGetResponse,
    AssignmentUpdate,
)
from course_service.web.schemas.base_schemas import Pagination
from course_service.web.schemas.errors import ErrorResponse

assignments_router = APIRouter(prefix="/api/v1/assignments", tags=["Assignments"])


@assignments_router.get(
    "/",
    response_model=AssignmentsGetResponse,
    responses={"401": {"model": ErrorResponse}},
)
async def list_assignments(
    repository: Annotated[AssignmentRepository, Depends(get_assignment_repository)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> AssignmentsGetResponse:
    page = await repository.list(offset=offset, limit=limit)
    return AssignmentsGetResponse(
        data=page.items,
        pagination=Pagination(offset=page.offset, limit=page.limit, total=page.total),
    )


@assignments_router.post(
    "/",
    response_model=Assignment,
    status_code=201,
    responses={
        "400": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
    },
)
async def create_assignment(
    body: AssignmentCreate,
    idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")],
    repositories: Annotated[RepositoryContainer, Depends(get_repositories)],
    idempotency: Annotated[IdempotencyRepository, Depends(get_idempotency_repository)],
) -> Assignment:
    if await repositories.courses.get(body.course_id) is None:
        raise HTTPException(400, "Course not found")
    key = str(idempotency_key)
    async with repositories.assignment_create_lock:
        existing_id = await idempotency.get("create_assignment", key)
        if existing_id is not None:
            existing = await repositories.assignments.get(existing_id)
            if existing is None:
                raise HTTPException(500, "Invalid idempotency reference")
            return existing
        now = datetime.now(UTC)
        assignment = Assignment(
            id=uuid4(), created_at=now, updated_at=now, **body.model_dump()
        )
        await repositories.assignments.create(assignment)
        await idempotency.save("create_assignment", key, assignment.id)
        return assignment


@assignments_router.get(
    "/{id}",
    response_model=Assignment,
    responses={"401": {"model": ErrorResponse}, "404": {"model": ErrorResponse}},
)
async def get_assignment(
    id: UUID,
    repository: Annotated[AssignmentRepository, Depends(get_assignment_repository)],
) -> Assignment:
    assignment = await repository.get(id)
    if assignment is None:
        raise HTTPException(404, "Assignment not found")
    return assignment


@assignments_router.patch(
    "/{id}",
    response_model=Assignment,
    responses={
        "400": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
        "404": {"model": ErrorResponse},
    },
)
async def update_assignment(
    id: UUID,
    body: AssignmentUpdate,
    repository: Annotated[AssignmentRepository, Depends(get_assignment_repository)],
) -> Assignment:
    assignment = await repository.get(id)
    if assignment is None:
        raise HTTPException(404, "Assignment not found")
    updated = assignment.model_copy(
        update=body.model_dump(exclude_unset=True), deep=True
    )
    updated.updated_at = datetime.now(UTC)
    return await repository.update(updated)


@assignments_router.delete(
    "/{id}",
    status_code=204,
    responses={
        "401": {"model": ErrorResponse},
        "403": {"model": ErrorResponse},
        "404": {"model": ErrorResponse},
    },
)
async def delete_assignment(
    id: UUID,
    repository: Annotated[AssignmentRepository, Depends(get_assignment_repository)],
) -> None:
    if not await repository.delete(id):
        raise HTTPException(404, "Assignment not found")
