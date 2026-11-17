from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Protocol, Self, TypeVar
from uuid import UUID

from course_service.infrastructure.persistence.repositories.pagination import Page
from course_service.web.schemas.assignments import Assignment
from course_service.web.schemas.courses import Course
from course_service.web.schemas.reviews import Review
from course_service.web.schemas.submissions import Artifact, Submission

T = TypeVar("T")


class CourseRepositoryPort(Protocol):
    async def get(self, course_id: UUID) -> Course | None: ...

    async def list(self, *, offset: int = 0, limit: int = 10) -> Page[Course]: ...

    async def create(self, course: Course) -> Course: ...

    async def update(self, course: Course) -> Course: ...

    async def delete(self, course_id: UUID) -> bool: ...


class AssignmentRepositoryPort(Protocol):
    async def get(self, assignment_id: UUID) -> Assignment | None: ...

    async def list(self, *, offset: int = 0, limit: int = 10) -> Page[Assignment]: ...

    async def create(self, assignment: Assignment) -> Assignment: ...

    async def update(self, assignment: Assignment) -> Assignment: ...

    async def delete(self, assignment_id: UUID) -> bool: ...


class SubmissionRepositoryPort(Protocol):
    async def get(self, submission_id: UUID) -> Submission | None: ...

    async def create(self, submission: Submission) -> Submission: ...

    async def update(self, submission: Submission) -> Submission: ...

    async def list_for_assignment(self, assignment_id: UUID) -> list[Submission]: ...

    async def attach_review(
        self, submission_id: UUID, review_id: UUID, review_type: str
    ) -> Submission | None: ...

    async def get_artifacts(self, submission_id: UUID) -> list[Artifact]: ...


class ReviewRepositoryPort(Protocol):
    async def get(self, review_id: UUID) -> Review | None: ...

    async def get_for_submission(self, submission_id: UUID) -> Review | None: ...

    async def create(self, review: Review) -> Review: ...

    async def update(self, review: Review) -> Review: ...


class IdempotencyRepositoryPort(Protocol):
    async def get(self, operation: str, key: str) -> UUID | None: ...

    async def save(self, operation: str, key: str, entity_id: UUID) -> None: ...


class IdempotencyPort(Protocol):
    async def execute(
        self,
        *,
        operation: str,
        key: str,
        find_result: Callable[[UUID], Awaitable[T | None]],
        create: Callable[[], Awaitable[T]],
        get_id: Callable[[T], UUID],
    ) -> T: ...


class EventPublisherPort(Protocol):
    async def publish(self, topic: str, payload: dict[str, object]) -> None: ...


class OutboxPort(Protocol):
    async def add(self, topic: str, payload: dict[str, object]) -> None: ...

    async def pending(self) -> list[OutboxMessage]: ...

    async def mark_published(self, message_id: int) -> None: ...

    async def begin(self) -> None: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...


@dataclass(frozen=True)
class OutboxMessage:
    id: int
    topic: str
    payload: dict[str, object]
    published: bool = False


class UnitOfWorkPort(Protocol):
    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self, exc_type: object, exc: object, traceback: object
    ) -> None: ...
