from typing import Annotated
from uuid import UUID

from pydantic import Field

from course_service.web.schemas.base_schemas import BaseSchemaModel


class ErrorDetails(BaseSchemaModel):
    code: Annotated[str, Field(examples=["COURSE_NOT_FOUND"])]
    message: Annotated[str, Field(examples=["Курс не существует"])]
    status: Annotated[int, Field(examples=[404])]
    path: Annotated[
        str, Field(examples=["/api/v1/courses/00000000-0000-0000-0000-000000000000"])
    ]
    request_id: Annotated[
        UUID, Field(examples=["88888888-8888-8888-8888-888888888888"])
    ]


class ErrorResponse(BaseSchemaModel):
    error: ErrorDetails
