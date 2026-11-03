from uuid import UUID

from course_service.web.schemas.assignments import Assignment
from course_service.web.schemas.courses import Course
from course_service.web.schemas.reviews import Review
from course_service.web.schemas.submissions import Submission


class InMemoryStore:
    def __init__(self) -> None:
        self.courses: dict[UUID, Course] = {}
        self.assignments: dict[UUID, Assignment] = {}
        self.submissions: dict[UUID, Submission] = {}
        self.reviews: dict[UUID, Review] = {}
        self.idempotency_keys: dict[tuple[str, str], UUID] = {}
