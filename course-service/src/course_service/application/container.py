from course_service.application.services import CourseService
from course_service.application.services.assignments import AssignmentService
from course_service.application.services.idempotency import IdempotencyService
from course_service.application.services.reviews import ReviewService
from course_service.application.services.submissions import SubmissionService
from course_service.infrastructure.messaging.dispatcher import OutboxDispatcher
from course_service.infrastructure.messaging.mock_kafka import MockKafkaPublisher
from course_service.infrastructure.persistence.outbox import InMemoryOutbox
from course_service.infrastructure.persistence.repositories import (
    AssignmentRepository,
    CourseRepository,
    IdempotencyRepository,
    KeyedLockRegistry,
    ReviewRepository,
    SubmissionRepository,
)
from course_service.infrastructure.persistence.store import InMemoryStore
from course_service.infrastructure.persistence.unit_of_work import InMemoryUnitOfWork


class ApplicationContainer:
    def __init__(self) -> None:
        store = InMemoryStore()

        self.courses = CourseRepository(store)
        self.assignments = AssignmentRepository(store)
        self.submissions = SubmissionRepository(store)
        self.reviews = ReviewRepository(store, self.submissions)
        self.idempotency = IdempotencyRepository(store)
        self.idempotency_locks = KeyedLockRegistry()
        self.outbox = InMemoryOutbox()
        self.unit_of_work = InMemoryUnitOfWork(store, self.outbox)
        self.kafka = MockKafkaPublisher()
        self.outbox_dispatcher = OutboxDispatcher(self.outbox, self.kafka)
        idempotency_service = IdempotencyService(
            self.idempotency, self.idempotency_locks
        )
        self.course_service = CourseService(self.courses, idempotency_service)
        self.assignment_service = AssignmentService(
            self.assignments, self.courses, idempotency_service
        )
        self.submission_service = SubmissionService(
            self.submissions,
            self.assignments,
            idempotency_service,
            self.outbox,
            self.unit_of_work,
        )
        self.review_service = ReviewService(
            self.reviews, self.submissions, idempotency_service
        )
