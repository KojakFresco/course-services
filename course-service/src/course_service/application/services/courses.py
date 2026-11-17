from datetime import UTC, datetime
from uuid import UUID, uuid4

from course_service.application.errors import CourseNotFoundError
from course_service.application.ports import CourseRepositoryPort, IdempotencyPort
from course_service.infrastructure.persistence.repositories.pagination import Page
from course_service.web.schemas.courses import Course, CourseCreate, CourseUpdate


class CourseService:
    def __init__(
        self,
        repository: CourseRepositoryPort,
        idempotency: IdempotencyPort,
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

    async def get(self, course_id: UUID) -> Course:
        course = await self._repository.get(course_id)
        if course is None:
            raise CourseNotFoundError
        return course

    async def list(self, *, offset: int = 0, limit: int = 10) -> Page[Course]:
        return await self._repository.list(offset=offset, limit=limit)

    async def update(self, course_id: UUID, body: CourseUpdate) -> Course:
        course = await self.get(course_id)
        updated = course.model_copy(
            update=body.model_dump(exclude_unset=True), deep=True
        )
        updated.updated_at = datetime.now(UTC)
        return await self._repository.update(updated)

    async def delete(self, course_id: UUID) -> None:
        if not await self._repository.delete(course_id):
            raise CourseNotFoundError
