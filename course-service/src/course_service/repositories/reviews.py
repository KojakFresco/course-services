import asyncio
from uuid import UUID

from course_service.repositories.memory import InMemoryStore
from course_service.web.schemas.reviews import Review


class ReviewRepository:
    def __init__(self, store: InMemoryStore | None = None) -> None:
        self._store = store or InMemoryStore()
        self._lock = asyncio.Lock()

    async def get(self, review_id: UUID) -> Review | None:
        async with self._lock:
            return self._store.reviews.get(review_id)

    async def list_for_submission(self, submission_id: UUID) -> list[Review]:
        async with self._lock:
            review_ids = self._store.reviews_by_submission.get(submission_id, [])
            return [
                self._store.reviews[review_id]
                for review_id in review_ids
                if review_id in self._store.reviews
            ]

    async def create(self, submission_id: UUID, review: Review) -> Review:
        async with self._lock:
            self._store.reviews[review.id] = review
            self._store.reviews_by_submission.setdefault(submission_id, []).append(
                review.id
            )
            return review

    async def update(self, review: Review) -> Review:
        async with self._lock:
            self._store.reviews[review.id] = review
            return review
