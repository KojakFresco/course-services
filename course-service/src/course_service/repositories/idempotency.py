import asyncio
from uuid import UUID

from course_service.repositories.memory import InMemoryStore


class IdempotencyRepository:
    def __init__(self, store: InMemoryStore | None = None) -> None:
        self._store = store or InMemoryStore()
        self._lock = asyncio.Lock()

    async def get(self, operation: str, key: str) -> UUID | None:
        async with self._lock:
            return self._store.idempotency_keys.get(f"{operation}:{key}")

    async def save(self, operation: str, key: str, entity_id: UUID) -> None:
        async with self._lock:
            self._store.idempotency_keys[f"{operation}:{key}"] = entity_id
