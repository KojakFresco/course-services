import logging
from collections.abc import Awaitable, Callable
from uuid import UUID, uuid4

from fastapi import Request, Response

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"


async def correlation_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    request_id = request.headers.get(REQUEST_ID_HEADER)

    try:
        UUID(request_id) if request_id else None
    except ValueError:
        request_id = None

    request_id = request_id or str(uuid4())
    request.state.request_id = request_id

    response = await call_next(request)

    response.headers[REQUEST_ID_HEADER] = request_id
    return response
