from typing import Annotated

from fastapi import Depends, Request

from course_service.application.container import ApplicationContainer
from course_service.application.errors import ApplicationNotConfiguredError
from course_service.application.services import CourseService
from course_service.application.services.assignments import AssignmentService
from course_service.application.services.reviews import ReviewService
from course_service.application.services.submissions import SubmissionService
from course_service.infrastructure.persistence.repositories import (
    AssignmentRepository,
    CourseRepository,
    IdempotencyRepository,
    ReviewRepository,
)
from course_service.infrastructure.persistence.repositories.submissions import (
    SubmissionRepository,
)


def get_application(request: Request) -> ApplicationContainer:
    application = getattr(request.app.state, "application", None)

    if not isinstance(application, ApplicationContainer):
        raise ApplicationNotConfiguredError("ApplicationContainer is not configured")

    return application


def get_course_repository(
    application: Annotated[ApplicationContainer, Depends(get_application)],
) -> CourseRepository:
    return application.courses


def get_assignment_repository(
    application: Annotated[ApplicationContainer, Depends(get_application)],
) -> AssignmentRepository:
    return application.assignments


def get_submission_repository(
    application: Annotated[ApplicationContainer, Depends(get_application)],
) -> SubmissionRepository:
    return application.submissions


def get_review_repository(
    application: Annotated[ApplicationContainer, Depends(get_application)],
) -> ReviewRepository:
    return application.reviews


def get_idempotency_repository(
    application: Annotated[ApplicationContainer, Depends(get_application)],
) -> IdempotencyRepository:
    return application.idempotency


def get_course_service(
    application: Annotated[ApplicationContainer, Depends(get_application)],
) -> CourseService:
    return application.course_service


def get_assignment_service(
    application: Annotated[ApplicationContainer, Depends(get_application)],
) -> AssignmentService:
    return application.assignment_service


def get_submission_service(
    application: Annotated[ApplicationContainer, Depends(get_application)],
) -> SubmissionService:
    return application.submission_service


def get_review_service(
    application: Annotated[ApplicationContainer, Depends(get_application)],
) -> ReviewService:
    return application.review_service
