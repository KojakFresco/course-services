from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import HTTPException

from course_service.repositories.assignments import AssignmentRepository
from course_service.repositories.courses import CourseRepository
from course_service.services.idempotency import IdempotencyService
from course_service.web.schemas.assignments import Assignment, AssignmentCreate


class AssignmentService:
    def __init__(
        self,
        repository: AssignmentRepository,
        courses: CourseRepository,
        idempotency: IdempotencyService,
    ) -> None:
        self._repository = repository
        self._courses = courses
        self._idempotency = idempotency

    async def create(self, body: AssignmentCreate, key: UUID) -> Assignment:
        if await self._courses.get(body.course_id) is None:
            raise HTTPException(400, "Course not found")

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
