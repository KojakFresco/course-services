from collections.abc import Awaitable, Callable
from typing import TypeVar
from uuid import UUID

from course_service.repositories.idempotency import IdempotencyRepository
from course_service.repositories.locks import KeyedLockRegistry

T = TypeVar("T")


class IdempotencyService:
    def __init__(
        self,
        repository: IdempotencyRepository,
        locks: KeyedLockRegistry,
    ) -> None:
        self._repository = repository
        self._locks = locks

    async def execute(
        self,
        *,
        operation: str,
        key: str,
        find_result: Callable[[UUID], Awaitable[T | None]],
        create: Callable[[], Awaitable[T]],
        get_id: Callable[[T], UUID],
    ) -> T:
        lock = await self._locks.get_lock(operation, key)
        async with lock:
            entity_id = await self._repository.get(operation, key)
            if entity_id is not None:
                result = await find_result(entity_id)
                if result is None:
                    raise RuntimeError("Invalid idempotency reference")
                return result

            result = await create()
            await self._repository.save(operation, key, get_id(result))
            return result
