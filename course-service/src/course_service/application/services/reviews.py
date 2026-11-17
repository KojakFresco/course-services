from datetime import UTC, datetime
from uuid import UUID, uuid4

from course_service.application.errors import (
    ReviewNotFoundError,
    SubmissionNotFoundError,
)
from course_service.application.ports import (
    IdempotencyPort,
    ReviewRepositoryPort,
    SubmissionRepositoryPort,
)
from course_service.web.schemas.reviews import Review, ReviewCreate, ReviewUpdate


class ReviewService:
    def __init__(
        self,
        repository: ReviewRepositoryPort,
        submissions: SubmissionRepositoryPort,
        idempotency: IdempotencyPort,
    ) -> None:
        self._repository = repository
        self._submissions = submissions
        self._idempotency = idempotency

    async def create(
        self, submission_id: UUID, body: ReviewCreate, key: UUID
    ) -> Review:
        if await self._submissions.get(submission_id) is None:
            raise SubmissionNotFoundError

        async def create_review() -> Review:
            now = datetime.now(UTC)
            review = await self._repository.create(
                Review(id=uuid4(), created_at=now, updated_at=now, **body.model_dump())
            )
            linked_submission = await self._submissions.attach_review(
                submission_id,
                review.id,
                body.type.value,
            )
            if linked_submission is None:
                raise RuntimeError("Submission disappeared while creating review")
            return review

        return await self._idempotency.execute(
            operation="create_review",
            key=str(key),
            find_result=self._repository.get,
            create=create_review,
            get_id=lambda review: review.id,
        )

    async def get_for_submission(self, submission_id: UUID) -> Review:
        if await self._submissions.get(submission_id) is None:
            raise SubmissionNotFoundError
        review = await self._repository.get_for_submission(submission_id)
        if review is None:
            raise ReviewNotFoundError
        return review

    async def update(self, submission_id: UUID, body: ReviewUpdate) -> Review:
        review = await self.get_for_submission(submission_id)
        updated = review.model_copy(
            update=body.model_dump(exclude_unset=True), deep=True
        )
        updated.updated_at = datetime.now(UTC)
        return await self._repository.update(updated)
