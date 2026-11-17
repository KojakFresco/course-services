from datetime import UTC, datetime
from uuid import UUID, uuid4

from course_service.application.errors import (
    AssignmentNotFoundError,
    SubmissionAttemptsLimitExceededError,
    SubmissionNotFoundError,
)
from course_service.application.ports import (
    AssignmentRepositoryPort,
    IdempotencyPort,
    OutboxPort,
    SubmissionRepositoryPort,
    UnitOfWorkPort,
)
from course_service.infrastructure.messaging.mock_kafka import (
    CHECKS_COMMAND_TOPIC,
    SIMILARITY_COMMAND_TOPIC,
)
from course_service.web.schemas.submissions import (
    Artifact,
    Submission,
    SubmissionCreate,
    SubmissionStatus,
)


class SubmissionService:
    def __init__(
        self,
        repository: SubmissionRepositoryPort,
        assignments: AssignmentRepositoryPort,
        idempotency: IdempotencyPort,
        outbox: OutboxPort,
        unit_of_work: UnitOfWorkPort,
    ) -> None:
        self._repository = repository
        self._assignments = assignments
        self._idempotency = idempotency
        self._outbox = outbox
        self._unit_of_work = unit_of_work

    async def create(self, body: SubmissionCreate, key: UUID) -> Submission:
        assignment = await self._assignments.get(body.assignment_id)
        if assignment is None:
            raise AssignmentNotFoundError

        attempts_limit = assignment.attempts_limit

        async def create_submission() -> Submission:
            attempts = await self._repository.list_for_assignment(body.assignment_id)
            if len(attempts) >= attempts_limit:
                raise SubmissionAttemptsLimitExceededError
            async with self._unit_of_work:
                submission = await self._repository.create(
                    Submission(
                        id=uuid4(),
                        assignment_id=body.assignment_id,
                        submitted_at=datetime.now(UTC),
                        repository_url=body.repository_url,
                        status=SubmissionStatus.SUBMITTED,
                    )
                )
                payload: dict[str, object] = {
                    "submission_id": str(submission.id),
                    "assignment_id": str(submission.assignment_id),
                    "repository_url": str(submission.repository_url),
                }
                await self._outbox.add(CHECKS_COMMAND_TOPIC, payload)
                await self._outbox.add(SIMILARITY_COMMAND_TOPIC, payload)
            return submission

        return await self._idempotency.execute(
            operation="create_submission",
            key=str(key),
            find_result=self._repository.get,
            create=create_submission,
            get_id=lambda submission: submission.id,
        )

    async def get(self, submission_id: UUID) -> Submission:
        submission = await self._repository.get(submission_id)
        if submission is None:
            raise SubmissionNotFoundError
        return submission

    async def get_artifacts(self, submission_id: UUID) -> list[Artifact]:
        await self.get(submission_id)
        return await self._repository.get_artifacts(submission_id)
