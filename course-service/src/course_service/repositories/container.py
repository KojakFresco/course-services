from course_service.repositories import (
    AssignmentRepository,
    CourseRepository,
    IdempotencyRepository,
    InMemoryStore,
    ReviewRepository,
    SubmissionRepository,
)
from course_service.repositories.locks import KeyedLockRegistry
from course_service.services.assignments import AssignmentService
from course_service.services.courses import CourseService
from course_service.services.idempotency import IdempotencyService
from course_service.services.reviews import ReviewService
from course_service.services.submissions import SubmissionService


class RepositoryContainer:
    def __init__(self) -> None:
        store = InMemoryStore()

        self.courses = CourseRepository(store)
        self.assignments = AssignmentRepository(store)
        self.submissions = SubmissionRepository(store)
        self.reviews = ReviewRepository(store)
        self.idempotency = IdempotencyRepository(store)
        self.idempotency_locks = KeyedLockRegistry()
        idempotency_service = IdempotencyService(
            self.idempotency, self.idempotency_locks
        )
        self.course_service = CourseService(self.courses, idempotency_service)
        self.assignment_service = AssignmentService(
            self.assignments, self.courses, idempotency_service
        )
        self.submission_service = SubmissionService(
            self.submissions, self.assignments, idempotency_service
        )
        self.review_service = ReviewService(
            self.reviews, self.submissions, idempotency_service
        )
