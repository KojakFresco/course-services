from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from course_service.repositories import AssignmentRepository
from course_service.services.assignments import AssignmentService
from course_service.web.dependencies import (
    get_assignment_repository,
    get_assignment_service,
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
    service: Annotated[AssignmentService, Depends(get_assignment_service)],
) -> Assignment:
    return await service.create(body, idempotency_key)


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
