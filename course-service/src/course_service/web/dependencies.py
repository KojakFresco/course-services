from typing import Annotated

from fastapi import Depends, Request

from course_service.repositories.assignments import AssignmentRepository
from course_service.repositories.container import RepositoryContainer
from course_service.repositories.courses import CourseRepository
from course_service.repositories.idempotency import IdempotencyRepository
from course_service.repositories.reviews import ReviewRepository
from course_service.repositories.submissions import SubmissionRepository
from course_service.services.assignments import AssignmentService
from course_service.services.courses import CourseService
from course_service.services.reviews import ReviewService
from course_service.services.submissions import SubmissionService


def get_repositories(request: Request) -> RepositoryContainer:
    repositories = getattr(request.app.state, "repositories", None)

    if not isinstance(repositories, RepositoryContainer):
        raise RuntimeError("RepositoryContainer is not configured")

    return repositories


def get_course_repository(
    repositories: Annotated[
        RepositoryContainer,
        Depends(get_repositories),
    ],
) -> CourseRepository:
    return repositories.courses


def get_assignment_repository(
    repositories: Annotated[RepositoryContainer, Depends(get_repositories)],
) -> AssignmentRepository:
    return repositories.assignments


def get_submission_repository(
    repositories: Annotated[RepositoryContainer, Depends(get_repositories)],
) -> SubmissionRepository:
    return repositories.submissions


def get_review_repository(
    repositories: Annotated[RepositoryContainer, Depends(get_repositories)],
) -> ReviewRepository:
    return repositories.reviews


def get_idempotency_repository(
    repositories: Annotated[RepositoryContainer, Depends(get_repositories)],
) -> IdempotencyRepository:
    return repositories.idempotency


def get_course_service(
    repositories: Annotated[RepositoryContainer, Depends(get_repositories)],
) -> CourseService:
    return repositories.course_service


def get_assignment_service(
    repositories: Annotated[RepositoryContainer, Depends(get_repositories)],
) -> AssignmentService:
    return repositories.assignment_service


def get_submission_service(
    repositories: Annotated[RepositoryContainer, Depends(get_repositories)],
) -> SubmissionService:
    return repositories.submission_service


def get_review_service(
    repositories: Annotated[RepositoryContainer, Depends(get_repositories)],
) -> ReviewService:
    return repositories.review_service
