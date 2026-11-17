from datetime import UTC, datetime
from uuid import UUID, uuid4

from course_service.application.errors import (
    AssignmentNotFoundError,
    CourseNotFoundError,
)
from course_service.application.ports import (
    AssignmentRepositoryPort,
    CourseRepositoryPort,
    IdempotencyPort,
)
from course_service.infrastructure.persistence.repositories.pagination import Page
from course_service.web.schemas.assignments import (
    Assignment,
    AssignmentCreate,
    AssignmentUpdate,
)


class AssignmentService:
    def __init__(
        self,
        repository: AssignmentRepositoryPort,
        courses: CourseRepositoryPort,
        idempotency: IdempotencyPort,
    ) -> None:
        self._repository = repository
        self._courses = courses
        self._idempotency = idempotency

    async def create(self, body: AssignmentCreate, key: UUID) -> Assignment:
        if await self._courses.get(body.course_id) is None:
            raise CourseNotFoundError

        async def create_assignment() -> Assignment:
            now = datetime.now(UTC)
            return await self._repository.create(
                Assignment(
                    id=uuid4(),
                    created_at=now,
                    updated_at=now,
                    **body.model_dump(),
                )
            )

        return await self._idempotency.execute(
            operation="create_assignment",
            key=str(key),
            find_result=self._repository.get,
            create=create_assignment,
            get_id=lambda assignment: assignment.id,
        )

    async def get(self, assignment_id: UUID) -> Assignment:
        assignment = await self._repository.get(assignment_id)
        if assignment is None:
            raise AssignmentNotFoundError
        return assignment

    async def list(self, *, offset: int = 0, limit: int = 10) -> Page[Assignment]:
        return await self._repository.list(offset=offset, limit=limit)

    async def update(self, assignment_id: UUID, body: AssignmentUpdate) -> Assignment:
        assignment = await self.get(assignment_id)
        updated = assignment.model_copy(
            update=body.model_dump(exclude_unset=True), deep=True
        )
        updated.updated_at = datetime.now(UTC)
        return await self._repository.update(updated)

    async def delete(self, assignment_id: UUID) -> None:
        if not await self._repository.delete(assignment_id):
            raise AssignmentNotFoundError
