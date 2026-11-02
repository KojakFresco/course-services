from course_service.web.schemas.base_schemas import ServiceInfo


def get_service_info() -> ServiceInfo:
    return ServiceInfo()
