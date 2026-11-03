from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import HTTPException

from course_service.repositories.assignments import AssignmentRepository
from course_service.repositories.submissions import SubmissionRepository
from course_service.services.idempotency import IdempotencyService
from course_service.web.schemas.submissions import (
    Submission,
    SubmissionCreate,
    SubmissionStatus,
)


class SubmissionService:
    def __init__(
        self,
        repository: SubmissionRepository,
        assignments: AssignmentRepository,
        idempotency: IdempotencyService,
    ) -> None:
        self._repository = repository
        self._assignments = assignments
        self._idempotency = idempotency

    async def create(self, body: SubmissionCreate, key: UUID) -> Submission:
        assignment = await self._assignments.get(body.assignment_id)
        if assignment is None:
            raise HTTPException(400, "Assignment not found")

        async def create_submission() -> Submission:
            attempts = await self._repository.list_for_assignment(body.assignment_id)
            if len(attempts) >= assignment.attempts_limit:
                raise HTTPException(409, "Submission attempts limit exceeded")
            return await self._repository.create(
                Submission(
                    id=uuid4(),
                    assignment_id=body.assignment_id,
                    submitted_at=datetime.now(UTC),
                    repository_url=body.repository_url,
                    status=SubmissionStatus.SUBMITTED,
                )
            )

        return await self._idempotency.execute(
            operation="create_submission",
            key=str(key),
            find_result=self._repository.get,
            create=create_submission,
            get_id=lambda submission: submission.id,
        )
