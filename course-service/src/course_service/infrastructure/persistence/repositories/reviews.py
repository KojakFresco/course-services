from uuid import UUID

from course_service.infrastructure.persistence.repositories.locks import ReadWriteLock
from course_service.infrastructure.persistence.repositories.submissions import (
    SubmissionRepository,
)
from course_service.infrastructure.persistence.store import InMemoryStore
from course_service.web.schemas.reviews import Review


class ReviewRepository:
    def __init__(
        self,
        store: InMemoryStore | None = None,
        submissions: SubmissionRepository | None = None,
    ) -> None:
        self._store = store or InMemoryStore()
        self._submissions = submissions or SubmissionRepository(self._store)
        self._lock = ReadWriteLock()

    async def get(self, review_id: UUID) -> Review | None:
        async with self._lock.read_lock():
            return self._store.reviews.get(review_id)

    async def get_for_submission(self, submission_id: UUID) -> Review | None:
        submission = await self._submissions.get(submission_id)
        if submission is None:
            return None

        review_id = submission.review_id or submission.auto_review_id
        return await self.get(review_id) if review_id is not None else None

    async def create(self, review: Review) -> Review:
        async with self._lock.write_lock():
            self._store.reviews[review.id] = review
            return review

    async def update(self, review: Review) -> Review:
        async with self._lock.write_lock():
            self._store.reviews[review.id] = review
            return review
