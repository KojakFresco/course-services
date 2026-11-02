from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException

from course_service.repositories import IdempotencyRepository, ReviewRepository
from course_service.repositories.container import RepositoryContainer
from course_service.web.dependencies import (
    get_idempotency_repository,
    get_repositories,
    get_review_repository,
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
    repositories: Annotated[RepositoryContainer, Depends(get_repositories)],
    repository: Annotated[ReviewRepository, Depends(get_review_repository)],
) -> Review:
    if await repositories.submissions.get(id) is None:
        raise HTTPException(404, "Submission not found")
    reviews = await repository.list_for_submission(id)
    if not reviews:
        raise HTTPException(404, "Review not found")
    return reviews[-1]


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
    repositories: Annotated[RepositoryContainer, Depends(get_repositories)],
    idempotency: Annotated[IdempotencyRepository, Depends(get_idempotency_repository)],
) -> Review:
    key = str(idempotency_key)
    async with repositories.review_create_lock:
        existing_id = await idempotency.get("create_review", key)
        if existing_id is not None:
            existing = await repositories.reviews.get(existing_id)
            if existing is None:
                raise HTTPException(500, "Invalid idempotency reference")
            return existing
        if await repositories.submissions.get(id) is None:
            raise HTTPException(404, "Submission not found")
        now = datetime.now(UTC)
        review = Review(id=uuid4(), created_at=now, updated_at=now, **body.model_dump())
        await repositories.reviews.create(id, review)
        await idempotency.save("create_review", key, review.id)
        return review


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
    repositories: Annotated[RepositoryContainer, Depends(get_repositories)],
    repository: Annotated[ReviewRepository, Depends(get_review_repository)],
) -> Review:
    if await repositories.submissions.get(id) is None:
        raise HTTPException(404, "Submission not found")
    reviews = await repository.list_for_submission(id)
    if not reviews:
        raise HTTPException(404, "Review not found")
    review = reviews[-1]
    updated = review.model_copy(update=body.model_dump(exclude_unset=True), deep=True)
    updated.updated_at = datetime.now(UTC)
    return await repository.update(updated)
