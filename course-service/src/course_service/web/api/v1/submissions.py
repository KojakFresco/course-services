from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException

from course_service.repositories import IdempotencyRepository, SubmissionRepository
from course_service.repositories.container import RepositoryContainer
from course_service.web.dependencies import (
    get_idempotency_repository,
    get_repositories,
    get_submission_repository,
)
from course_service.web.schemas.errors import ErrorResponse
from course_service.web.schemas.submissions import (
    Artifact,
    Submission,
    SubmissionCreate,
    SubmissionStatus,
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
    repositories: Annotated[RepositoryContainer, Depends(get_repositories)],
    idempotency: Annotated[IdempotencyRepository, Depends(get_idempotency_repository)],
) -> Submission:
    key = str(idempotency_key)
    async with repositories.submission_create_lock:
        existing_id = await idempotency.get("create_submission", key)
        if existing_id is not None:
            existing = await repositories.submissions.get(existing_id)
            if existing is None:
                raise HTTPException(500, "Invalid idempotency reference")
            return existing
        assignment = await repositories.assignments.get(body.assignment_id)
        if assignment is None:
            raise HTTPException(400, "Assignment not found")
        attempts = await repositories.submissions.list_for_assignment(
            body.assignment_id
        )
        if len(attempts) >= assignment.attempts_limit:
            raise HTTPException(409, "Submission attempts limit exceeded")
        submission = Submission(
            id=uuid4(),
            assignment_id=body.assignment_id,
            submitted_at=datetime.now(UTC),
            repository_url=body.repository_url,
            status=SubmissionStatus.SUBMITTED,
        )
        await repositories.submissions.create(submission)
        await idempotency.save("create_submission", key, submission.id)
        return submission


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
