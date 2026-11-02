from fastapi import APIRouter

from course_service.core.services import get_service_info
from course_service.web.lifespans import lifespan_service_router
from course_service.web.schemas.base_schemas import ServiceInfo

service_router = APIRouter(
    prefix="/service", lifespan=lifespan_service_router, tags=["service"]
)


@service_router.get(
    "/", description="Service info route", response_model=ServiceInfo, status_code=200
)
def info() -> ServiceInfo:
    return get_service_info()
