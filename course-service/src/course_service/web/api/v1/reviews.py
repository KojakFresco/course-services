from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException

from course_service.application.container import ApplicationContainer
from course_service.repositories import ReviewRepository
from course_service.services.reviews import ReviewService
from course_service.web.dependencies import (
    get_application,
    get_review_repository,
    get_review_service,
)
from course_service.web.schemas.errors import ErrorResponse
from course_service.web.schemas.reviews import Review, ReviewCreate, ReviewUpdate

reviews_router = APIRouter(prefix="/api/v1/submissions/{id}/review", tags=["Reviews"])


@reviews_router.get(
    "/",
    response_model=Review,
    responses={"401": {"model": ErrorResponse}, "404": {"model": ErrorResponse}},
)
async def get_submission_review(
    id: UUID,
    application: Annotated[ApplicationContainer, Depends(get_application)],
    repository: Annotated[ReviewRepository, Depends(get_review_repository)],
) -> Review:
    if await application.submissions.get(id) is None:
        raise HTTPException(404, "Submission not found")
    review = await repository.get_for_submission(id)
    if review is None:
        raise HTTPException(404, "Review not found")
    return review


@reviews_router.post(
    "/",
    response_model=Review,
    status_code=201,
    responses={
        "400": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "404": {"model": ErrorResponse},
    },
)
async def create_submission_review(
    id: UUID,
    body: ReviewCreate,
    idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")],
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> Review:
    return await service.create(id, body, idempotency_key)


@reviews_router.patch(
    "/",
    response_model=Review,
    responses={
        "400": {"model": ErrorResponse},
        "401": {"model": ErrorResponse},
        "404": {"model": ErrorResponse},
    },
)
async def update_submission_review(
    id: UUID,
    body: ReviewUpdate,
    application: Annotated[ApplicationContainer, Depends(get_application)],
    repository: Annotated[ReviewRepository, Depends(get_review_repository)],
) -> Review:
    if await application.submissions.get(id) is None:
        raise HTTPException(404, "Submission not found")
    review = await repository.get_for_submission(id)
    if review is None:
        raise HTTPException(404, "Review not found")
    updated = review.model_copy(update=body.model_dump(exclude_unset=True), deep=True)
    updated.updated_at = datetime.now(UTC)
    return await repository.update(updated)
