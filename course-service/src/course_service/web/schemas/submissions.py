from enum import Enum
from typing import Annotated
from uuid import UUID

from pydantic import AnyUrl, AwareDatetime, Field

from course_service.web.schemas.base_schemas import BaseSchemaModel


class SubmissionCreate(BaseSchemaModel):
    assignment_id: Annotated[
        UUID, Field(examples=["55555555-5555-5555-5555-555555555555"])
    ]
    repository_url: Annotated[
        AnyUrl, Field(examples=["https://github.com/student/lab2-solution"])
    ]


class SubmissionStatus(Enum):
    SUBMITTED = "SUBMITTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Submission(BaseSchemaModel):
    id: Annotated[UUID, Field(examples=["aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"])]
    assignment_id: Annotated[
        UUID, Field(examples=["55555555-5555-5555-5555-555555555555"])
    ]
    submitted_at: Annotated[AwareDatetime, Field(examples=["2026-10-15T18:24:01Z"])]
    review_id: Annotated[
        UUID | None,
        Field(
            description="ID связанной проверки (заполняется после ревью преподавателем)",
            examples=["cccccccc-cccc-cccc-cccc-cccccccccccc"],
        ),
    ] = None
    auto_review_id: Annotated[
        UUID | None,
        Field(
            description="ID автоматической проверки (если запускались тесты)",
            examples=["bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"],
        ),
    ] = None
    repository_url: Annotated[
        AnyUrl, Field(examples=["https://github.com/student/lab2-solution"])
    ]
    status: Annotated[SubmissionStatus, Field(examples=["SUBMITTED"])]
    artifacts_url: Annotated[
        AnyUrl | None,
        Field(
            description="Ссылка на артефакты решения",
            examples=["https://storage.university.com/artifacts/lab2/student1.zip"],
        ),
    ] = None


class Artifact(BaseSchemaModel):
    artifacts_url: Annotated[
        AnyUrl,
        Field(examples=["https://storage.university.com/artifacts/lab2/student1.zip"]),
    ]
