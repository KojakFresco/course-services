from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException

from course_service.repositories import SubmissionRepository
from course_service.services.submissions import SubmissionService
from course_service.web.dependencies import (
    get_submission_repository,
    get_submission_service,
)
from course_service.web.schemas.errors import ErrorResponse
from course_service.web.schemas.submissions import (
    Artifact,
    Submission,
    SubmissionCreate,
)

submissions_router = APIRouter(prefix="/api/v1/submissions", tags=["Submissions"])


@submissions_router.post(
    "/",
    response_model=Submission,
    status_code=201,
    responses={
        "400": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "409": {"model": ErrorResponse},
    },
)
async def create_submission(
    body: SubmissionCreate,
    idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")],
    service: Annotated[SubmissionService, Depends(get_submission_service)],
) -> Submission:
    return await service.create(body, idempotency_key)


@submissions_router.get(
    "/{id}",
    response_model=Submission,
    responses={"401": {"model": ErrorResponse}, "404": {"model": ErrorResponse}},
)
async def get_submission(
    id: UUID,
    repository: Annotated[SubmissionRepository, Depends(get_submission_repository)],
) -> Submission:
    submission = await repository.get(id)
    if submission is None:
        raise HTTPException(404, "Submission not found")
    return submission


@submissions_router.get(
    "/{id}/artifacts",
    response_model=list[Artifact],
    responses={"401": {"model": ErrorResponse}, "404": {"model": ErrorResponse}},
)
async def get_submission_artifacts(
    id: UUID,
    repository: Annotated[SubmissionRepository, Depends(get_submission_repository)],
) -> list[Artifact]:
    if await repository.get(id) is None:
        raise HTTPException(404, "Submission not found")
    return await repository.get_artifacts(id)
