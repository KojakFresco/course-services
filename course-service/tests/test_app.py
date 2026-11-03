from uuid import uuid4

import pytest

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
