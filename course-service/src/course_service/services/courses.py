from datetime import UTC, datetime
from uuid import UUID, uuid4

from course_service.repositories.courses import CourseRepository
from course_service.services.idempotency import IdempotencyService
from course_service.web.schemas.courses import Course, CourseCreate


class CourseService:
    def __init__(
        self,
        repository: CourseRepository,
        idempotency: IdempotencyService,
    ) -> None:
        self._repository = repository
        self._idempotency = idempotency

    async def create(self, body: CourseCreate, key: UUID) -> Course:
        async def create_course() -> Course:
            now = datetime.now(UTC)
            return await self._repository.create(
                Course(id=uuid4(), created_at=now, updated_at=now, **body.model_dump())
            )

        return await self._idempotency.execute(
            operation="create_course",
            key=str(key),
            find_result=self._repository.get,
            create=create_course,
            get_id=lambda course: course.id,
        )
