from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import HTTPException

from course_service.repositories.reviews import ReviewRepository
from course_service.repositories.submissions import SubmissionRepository
from course_service.services.idempotency import IdempotencyService
from course_service.web.schemas.reviews import Review, ReviewCreate


class ReviewService:
    def __init__(
        self,
        repository: ReviewRepository,
        submissions: SubmissionRepository,
        idempotency: IdempotencyService,
    ) -> None:
        self._repository = repository
        self._submissions = submissions
        self._idempotency = idempotency

    async def create(
        self, submission_id: UUID, body: ReviewCreate, key: UUID
    ) -> Review:
        if await self._submissions.get(submission_id) is None:
            raise HTTPException(404, "Submission not found")

        async def create_review() -> Review:
            now = datetime.now(UTC)
            return await self._repository.create(
                submission_id,
                Review(id=uuid4(), created_at=now, updated_at=now, **body.model_dump()),
            )

        return await self._idempotency.execute(
            operation="create_review",
            key=str(key),
            find_result=self._repository.get,
            create=create_review,
            get_id=lambda review: review.id,
        )
