from fastapi import APIRouter

from course_service.web.api.v1.assignments import assignments_router
from course_service.web.api.v1.courses import courses_router
from course_service.web.api.v1.reviews import reviews_router
from course_service.web.api.v1.service import service_router
from course_service.web.api.v1.submissions import submissions_router

api_router = APIRouter()
api_router.include_router(assignments_router)
api_router.include_router(courses_router)
api_router.include_router(submissions_router)
api_router.include_router(reviews_router)
api_router.include_router(service_router)

__all__ = [
    "api_router",
    "assignments_router",
    "courses_router",
    "reviews_router",
    "service_router",
    "submissions_router",
]
