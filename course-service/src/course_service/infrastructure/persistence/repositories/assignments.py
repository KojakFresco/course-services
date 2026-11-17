from uuid import UUID

from course_service.infrastructure.persistence.repositories.locks import ReadWriteLock
from course_service.infrastructure.persistence.repositories.pagination import Page
from course_service.infrastructure.persistence.store import InMemoryStore
from course_service.web.schemas.assignments import Assignment


class AssignmentRepository:
    def __init__(self, store: InMemoryStore | None = None) -> None:
        self._store = store or InMemoryStore()
        self._lock = ReadWriteLock()

    async def get(self, assignment_id: UUID) -> Assignment | None:
        async with self._lock.read_lock():
            return self._store.assignments.get(assignment_id)

    async def list(self, *, offset: int = 0, limit: int = 10) -> Page[Assignment]:
        async with self._lock.read_lock():
            assignments = list(self._store.assignments.values())
            return Page(
                items=assignments[offset : offset + limit],
                total=len(assignments),
                offset=offset,
                limit=limit,
            )

    async def create(self, assignment: Assignment) -> Assignment:
        async with self._lock.write_lock():
            self._store.assignments[assignment.id] = assignment
            return assignment

    async def update(self, assignment: Assignment) -> Assignment:
        async with self._lock.write_lock():
            self._store.assignments[assignment.id] = assignment
            return assignment

    async def delete(self, assignment_id: UUID) -> bool:
        async with self._lock.write_lock():
            return self._store.assignments.pop(assignment_id, None) is not None
