import asyncio

from course_service.repositories import (
    AssignmentRepository,
    CourseRepository,
    IdempotencyRepository,
    InMemoryStore,
    ReviewRepository,
    SubmissionRepository,
)


class RepositoryContainer:
    def __init__(self) -> None:
        store = InMemoryStore()

        self.courses = CourseRepository(store)
        self.assignments = AssignmentRepository(store)
        self.submissions = SubmissionRepository(store)
        self.reviews = ReviewRepository(store)
        self.idempotency = IdempotencyRepository(store)
        self.course_create_lock = asyncio.Lock()
        self.assignment_create_lock = asyncio.Lock()
        self.submission_create_lock = asyncio.Lock()
        self.review_create_lock = asyncio.Lock()
