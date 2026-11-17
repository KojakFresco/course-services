from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Header

from course_service.application.container import ApplicationContainer
from course_service.application.services.submissions import SubmissionService
from course_service.web.dependencies import (
    get_application,
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
    application: Annotated[ApplicationContainer, Depends(get_application)],
    background_tasks: BackgroundTasks,
) -> Submission:
    submission = await service.create(body, idempotency_key)
    background_tasks.add_task(application.outbox_dispatcher.publish_pending)
    return submission


@submissions_router.get(
    "/{id}",
    response_model=Submission,
    responses={"401": {"model": ErrorResponse}, "404": {"model": ErrorResponse}},
)
async def get_submission(
    id: UUID,
    service: Annotated[SubmissionService, Depends(get_submission_service)],
) -> Submission:
    return await service.get(id)


@submissions_router.get(
    "/{id}/artifacts",
    response_model=list[Artifact],
    responses={"401": {"model": ErrorResponse}, "404": {"model": ErrorResponse}},
)
async def get_submission_artifacts(
    id: UUID,
    service: Annotated[SubmissionService, Depends(get_submission_service)],
) -> list[Artifact]:
    return await service.get_artifacts(id)
