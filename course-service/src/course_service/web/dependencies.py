from typing import Annotated

from fastapi import Depends, Request

from course_service.application.container import ApplicationContainer
from course_service.repositories.assignments import AssignmentRepository
from course_service.repositories.courses import CourseRepository
from course_service.repositories.idempotency import IdempotencyRepository
from course_service.repositories.reviews import ReviewRepository
from course_service.repositories.submissions import SubmissionRepository
from course_service.services.assignments import AssignmentService
from course_service.services.courses import CourseService
from course_service.services.reviews import ReviewService
from course_service.services.submissions import SubmissionService


def get_application(request: Request) -> ApplicationContainer:
    application = getattr(request.app.state, "application", None)

    if not isinstance(application, ApplicationContainer):
        raise RuntimeError("ApplicationContainer is not configured")

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
