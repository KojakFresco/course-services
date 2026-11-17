from copy import deepcopy
from dataclasses import dataclass
from uuid import UUID

from course_service.web.schemas.assignments import Assignment
from course_service.web.schemas.courses import Course
from course_service.web.schemas.reviews import Review
from course_service.web.schemas.submissions import Submission


@dataclass(frozen=True)
class StoreSnapshot:
    courses: dict[UUID, Course]
    assignments: dict[UUID, Assignment]
    submissions: dict[UUID, Submission]
    reviews: dict[UUID, Review]
    idempotency_keys: dict[tuple[str, str], UUID]


class InMemoryStore:
    def __init__(self) -> None:
        self.courses: dict[UUID, Course] = {}
        self.assignments: dict[UUID, Assignment] = {}
        self.submissions: dict[UUID, Submission] = {}
        self.reviews: dict[UUID, Review] = {}
        self.idempotency_keys: dict[tuple[str, str], UUID] = {}

    def snapshot(self) -> StoreSnapshot:
        return StoreSnapshot(
            courses=deepcopy(self.courses),
            assignments=deepcopy(self.assignments),
            submissions=deepcopy(self.submissions),
            reviews=deepcopy(self.reviews),
            idempotency_keys=deepcopy(self.idempotency_keys),
        )

    def restore(self, snapshot: StoreSnapshot) -> None:
        self.courses = snapshot.courses
        self.assignments = snapshot.assignments
        self.submissions = snapshot.submissions
        self.reviews = snapshot.reviews
        self.idempotency_keys = snapshot.idempotency_keys
