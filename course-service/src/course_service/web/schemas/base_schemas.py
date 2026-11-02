from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class BaseSchemaModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True, validate_assignment=True, populate_by_name=True
    )


class ServiceInfo(BaseSchemaModel):
    healthy: bool = True


class Pagination(BaseSchemaModel):
    offset: Annotated[int, Field(examples=[0])]
    limit: Annotated[int, Field(examples=[10])]
    total: Annotated[int, Field(examples=[42])]
