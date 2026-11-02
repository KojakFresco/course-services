from uuid import UUID

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def request_id_from(request: Request) -> UUID:
    return UUID(request.state.request_id)


def error_response(
    request: Request,
    *,
    code: str,
    message: str,
    status: int,
) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "error": {
                "code": code,
                "message": message,
                "status": status,
                "path": request.url.path,
                "request_id": str(request_id_from(request)),
            }
        },
        headers={"X-Request-ID": request.state.request_id},
    )


async def http_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, StarletteHTTPException):
        raise TypeError("Expected StarletteHTTPException")

    return error_response(
        request,
        code=f"HTTP_{exc.status_code}",
        message=str(exc.detail),
        status=exc.status_code,
    )


async def validation_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, RequestValidationError):
        raise TypeError("Expected RequestValidationError")

    return error_response(
        request,
        code="VALIDATION_ERROR",
        message="Request validation failed",
        status=422,
    )


async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return error_response(
        request,
        code="INTERNAL_SERVER_ERROR",
        message="Internal server error",
        status=500,
    )
