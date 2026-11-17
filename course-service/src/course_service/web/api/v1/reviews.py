from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header

from course_service.application.services.reviews import ReviewService
from course_service.web.dependencies import (
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
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> Review:
    return await service.get_for_submission(id)


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
    service: Annotated[ReviewService, Depends(get_review_service)],
) -> Review:
    return await service.update(id, body)
