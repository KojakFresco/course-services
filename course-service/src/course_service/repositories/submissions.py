import asyncio
from uuid import UUID

from course_service.repositories.memory import InMemoryStore
from course_service.web.schemas.submissions import Artifact, Submission


class SubmissionRepository:
    def __init__(self, store: InMemoryStore | None = None) -> None:
        self._store = store or InMemoryStore()
        self._lock = asyncio.Lock()

    async def get(self, submission_id: UUID) -> Submission | None:
        async with self._lock:
            return self._store.submissions.get(submission_id)

    async def create(self, submission: Submission) -> Submission:
        async with self._lock:
            self._store.submissions[submission.id] = submission
            return submission

    async def list_for_assignment(self, assignment_id: UUID) -> list[Submission]:
        async with self._lock:
            return [
                submission
                for submission in self._store.submissions.values()
                if submission.assignment_id == assignment_id
            ]

    async def update(self, submission: Submission) -> Submission:
        async with self._lock:
            self._store.submissions[submission.id] = submission
            return submission

    async def get_artifacts(self, submission_id: UUID) -> list[Artifact]:
        async with self._lock:
            submission = self._store.submissions.get(submission_id)
            if submission is None or submission.artifacts_url is None:
                return []
            return [Artifact(artifacts_url=submission.artifacts_url)]
