from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Self, TypeVar
from uuid import UUID, uuid4

import pytest

from course_service.application.ports import OutboxMessage
from course_service.application.services.submissions import SubmissionService
from course_service.infrastructure.persistence.outbox import InMemoryOutbox
from course_service.infrastructure.persistence.repositories.pagination import Page
from course_service.infrastructure.persistence.store import InMemoryStore
from course_service.infrastructure.persistence.unit_of_work import InMemoryUnitOfWork
from course_service.web.schemas.assignments import Assignment
from course_service.web.schemas.submissions import (
    Artifact,
    Submission,
    SubmissionCreate,
    SubmissionStatus,
)

TTest = TypeVar("TTest")

COURSE = {
    "title": "Backend-разработка на Python",
    "description": (
        "Полный курс по разработке серверных приложений и проектированию REST API."
    ),
    "teacher_id": "11111111-1111-1111-1111-111111111111",
    "status": "ACTIVE",
}
ASSIGNMENT = {
    "title": "Лабораторная работа №2 по REST API",
    "description": "Разработать и задокументировать контракты в формате OpenAPI",
    "attempts_limit": 3,
    "date_start": "2026-10-01",
    "date_end": "2026-10-20",
}
SUBMISSION = {
    "repository_url": "https://github.com/student/lab2-solution",
}
REVIEW = {
    "type": "manual",
    "feedback": "Обработка ошибок реализована корректно.",
    "mark": 9.5,
    "status": "PASSED",
}


def key() -> str:
    return str(uuid4())


def test_service_and_api_metadata(app_client):
    service_response = app_client.get("/service")
    assert service_response.status_code == 200
    assert service_response.json() == {"healthy": True}
    assert "X-Request-ID" in service_response.headers

    openapi_response = app_client.get("/openapi.json")
    assert openapi_response.status_code == 200
    assert openapi_response.json()["openapi"] == "3.1.0"

    docs_response = app_client.get("/docs")
    assert docs_response.status_code == 200


def test_courses_crud_and_pagination(app_client):
    response = app_client.get("/api/v1/courses")
    assert response.status_code == 200
    assert response.json()["pagination"] == {"offset": 0, "limit": 10, "total": 0}

    created = app_client.post(
        "/api/v1/courses",
        json=COURSE,
        headers={"Idempotency-Key": key()},
    )
    assert created.status_code == 201
    course = created.json()
    course_id = course["id"]

    listed = app_client.get("/api/v1/courses?offset=0&limit=1")
    assert listed.status_code == 200
    assert listed.json()["pagination"]["total"] == 1
    assert listed.json()["data"][0]["id"] == course_id

    fetched = app_client.get(f"/api/v1/courses/{course_id}")
    assert fetched.status_code == 200

    updated = app_client.patch(
        f"/api/v1/courses/{course_id}",
        json={"status": "CLOSED"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "CLOSED"

    deleted = app_client.delete(f"/api/v1/courses/{course_id}")
    assert deleted.status_code == 204
    assert app_client.get(f"/api/v1/courses/{course_id}").status_code == 404


def test_assignment_crud(app_client):
    course = app_client.post(
        "/api/v1/courses",
        json=COURSE,
        headers={"Idempotency-Key": key()},
    ).json()
    payload = {**ASSIGNMENT, "course_id": course["id"]}

    created = app_client.post(
        "/api/v1/assignments",
        json=payload,
        headers={"Idempotency-Key": key()},
    )
    assert created.status_code == 201
    assignment_id = created.json()["id"]

    assert app_client.get("/api/v1/assignments").status_code == 200
    assert app_client.get(f"/api/v1/assignments/{assignment_id}").status_code == 200
    assert (
        app_client.patch(
            f"/api/v1/assignments/{assignment_id}",
            json={"attempts_limit": 5},
        ).status_code
        == 200
    )
    assert app_client.delete(f"/api/v1/assignments/{assignment_id}").status_code == 204


def test_submissions_and_reviews(app_client):
    course = app_client.post(
        "/api/v1/courses",
        json=COURSE,
        headers={"Idempotency-Key": key()},
    ).json()
    assignment = app_client.post(
        "/api/v1/assignments",
        json={**ASSIGNMENT, "course_id": course["id"]},
        headers={"Idempotency-Key": key()},
    ).json()

    submission_response = app_client.post(
        "/api/v1/submissions",
        json={**SUBMISSION, "assignment_id": assignment["id"]},
        headers={"Idempotency-Key": key()},
    )
    assert submission_response.status_code == 201
    submission_id = submission_response.json()["id"]
    published_topics = [
        message.topic for message in app_client.app.state.application.kafka.messages
    ]
    assert published_topics == ["checks.command", "similarity.command"]

    assert app_client.get(f"/api/v1/submissions/{submission_id}").status_code == 200
    assert (
        app_client.get(f"/api/v1/submissions/{submission_id}/artifacts").status_code
        == 200
    )

    review_response = app_client.post(
        f"/api/v1/submissions/{submission_id}/review",
        json=REVIEW,
        headers={"Idempotency-Key": key()},
    )
    assert review_response.status_code == 201
    review_id = review_response.json()["id"]
    submission_after_review = app_client.get(
        f"/api/v1/submissions/{submission_id}"
    ).json()
    assert submission_after_review["review_id"] == review_id
    assert submission_after_review["auto_review_id"] is None
    review = app_client.get(f"/api/v1/submissions/{submission_id}/review")
    assert review.status_code == 200
    assert review.json()["id"] == review_id

    updated = app_client.patch(
        f"/api/v1/submissions/{submission_id}/review",
        json={"mark": 10},
    )
    assert updated.status_code == 200
    assert updated.json()["mark"] == 10


def test_idempotency_returns_same_course(app_client):
    idempotency_key = key()
    first = app_client.post(
        "/api/v1/courses",
        json=COURSE,
        headers={"Idempotency-Key": idempotency_key},
    )
    second = app_client.post(
        "/api/v1/courses",
        json=COURSE,
        headers={"Idempotency-Key": idempotency_key},
    )

    assert first.status_code == second.status_code == 201
    assert first.json()["id"] == second.json()["id"]


def test_submission_idempotency_does_not_duplicate_kafka_commands(app_client):
    course = app_client.post(
        "/api/v1/courses",
        json=COURSE,
        headers={"Idempotency-Key": key()},
    ).json()
    assignment = app_client.post(
        "/api/v1/assignments",
        json={**ASSIGNMENT, "course_id": course["id"]},
        headers={"Idempotency-Key": key()},
    ).json()
    idempotency_key = key()
    payload = {**SUBMISSION, "assignment_id": assignment["id"]}

    first = app_client.post(
        "/api/v1/submissions",
        json=payload,
        headers={"Idempotency-Key": idempotency_key},
    )
    second = app_client.post(
        "/api/v1/submissions",
        json=payload,
        headers={"Idempotency-Key": idempotency_key},
    )

    assert first.status_code == second.status_code == 201
    assert len(app_client.app.state.application.kafka.messages) == 2


@pytest.mark.asyncio
async def test_unit_of_work_rolls_back_submission_and_outbox():
    store = InMemoryStore()
    outbox = InMemoryOutbox()
    unit_of_work = InMemoryUnitOfWork(store, outbox)

    with pytest.raises(RuntimeError, match="rollback"):
        async with unit_of_work:
            submission = Submission.model_validate(
                {
                    "id": uuid4(),
                    "assignment_id": uuid4(),
                    "submitted_at": datetime.now(UTC),
                    "repository_url": "https://github.com/student/solution",
                    "status": SubmissionStatus.SUBMITTED,
                }
            )
            store.submissions[submission.id] = submission
            await outbox.add("checks.command", {"submission_id": "test"})
            raise RuntimeError("rollback")

    assert store.submissions == {}
    assert await outbox.pending() == []


@pytest.mark.asyncio
async def test_submission_service_isolated_from_fastapi_and_repositories():
    assignment_id = uuid4()
    assignment = Assignment.model_validate(
        {
            **ASSIGNMENT,
            "id": assignment_id,
            "course_id": uuid4(),
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
    )
    created: list[Submission] = []
    published: list[str] = []

    class FakeAssignments:
        async def get(self, requested_id: UUID) -> Assignment | None:
            return assignment if requested_id == assignment_id else None

        async def list(self, *, offset: int = 0, limit: int = 10) -> Page[Assignment]:
            return Page(items=[assignment], total=1, offset=offset, limit=limit)

        async def create(self, item: Assignment) -> Assignment:
            return item

        async def update(self, item: Assignment) -> Assignment:
            return item

        async def delete(self, requested_id: UUID) -> bool:
            return requested_id == assignment_id

    class FakeSubmissions:
        async def get(self, submission_id: UUID) -> Submission | None:
            return next((item for item in created if item.id == submission_id), None)

        async def list_for_assignment(self, requested_id: UUID) -> list[Submission]:
            return [item for item in created if item.assignment_id == requested_id]

        async def create(self, submission: Submission) -> Submission:
            created.append(submission)
            return submission

        async def update(self, submission: Submission) -> Submission:
            return submission

        async def attach_review(
            self, submission_id: UUID, review_id: UUID, review_type: str
        ) -> Submission | None:
            return await self.get(submission_id)

        async def get_artifacts(self, submission_id: UUID) -> list[Artifact]:
            return []

    class FakeIdempotency:
        async def execute(
            self,
            *,
            operation: str,
            key: str,
            find_result: Callable[[UUID], Awaitable[TTest | None]],
            create: Callable[[], Awaitable[TTest]],
            get_id: Callable[[TTest], UUID],
        ) -> TTest:
            return await create()

    class FakeOutbox:
        async def begin(self) -> None:
            return None

        async def commit(self) -> None:
            return None

        async def rollback(self) -> None:
            return None

        async def add(self, topic: str, payload: dict[str, object]) -> None:
            published.append(topic)

        async def pending(self) -> list[OutboxMessage]:
            return []

        async def mark_published(self, message_id: int) -> None:
            return None

    class FakeUnitOfWork:
        async def __aenter__(self) -> Self:
            return self

        async def __aexit__(
            self, exc_type: object, exc: object, traceback: object
        ) -> None:
            return None

    service = SubmissionService(
        FakeSubmissions(),
        FakeAssignments(),
        FakeIdempotency(),
        FakeOutbox(),
        FakeUnitOfWork(),
    )

    result = await service.create(
        SubmissionCreate.model_validate(
            {
                "assignment_id": assignment_id,
                "repository_url": "https://github.com/student/solution",
            }
        ),
        uuid4(),
    )

    assert result in created
    assert published == ["checks.command", "similarity.command"]


@pytest.mark.parametrize(
    ("path", "method"),
    (
        ("/api/v1/courses", "post"),
        ("/api/v1/assignments", "post"),
        ("/api/v1/submissions", "post"),
    ),
)
def test_idempotency_key_is_required(app_client, path, method):
    response = getattr(app_client, method)(path, json={})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_not_found_and_invalid_pagination_are_contract_errors(app_client):
    missing = app_client.get(f"/api/v1/courses/{uuid4()}")
    assert missing.status_code == 404
    assert missing.json()["error"]["status"] == 404

    invalid = app_client.get("/api/v1/courses?offset=-1")
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "VALIDATION_ERROR"
