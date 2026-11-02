import asyncio
from uuid import UUID

from course_service.repositories.memory import InMemoryStore
from course_service.repositories.pagination import Page
from course_service.web.schemas.courses import Course


class CourseRepository:
    def __init__(self, store: InMemoryStore | None = None) -> None:
        self._store = store or InMemoryStore()
        self._lock = asyncio.Lock()

    async def get(self, course_id: UUID) -> Course | None:
        async with self._lock:
            return self._store.courses.get(course_id)

    async def list(self, *, offset: int = 0, limit: int = 10) -> Page[Course]:
        async with self._lock:
            courses = list(self._store.courses.values())
            total = len(courses)

            return Page(
                items=courses[offset : offset + limit],
                total=total,
                offset=offset,
                limit=limit,
            )

    async def create(self, course: Course) -> Course:
        async with self._lock:
            self._store.courses[course.id] = course
            return course

    async def update(self, course: Course) -> Course:
        async with self._lock:
            self._store.courses[course.id] = course
            return course

    async def delete(self, course_id: UUID) -> bool:
        async with self._lock:
            return self._store.courses.pop(course_id, None) is not None
