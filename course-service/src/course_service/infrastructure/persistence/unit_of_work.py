import asyncio
from typing import Self

from course_service.application.ports import OutboxPort
from course_service.infrastructure.persistence.store import InMemoryStore, StoreSnapshot


class InMemoryUnitOfWork:
    def __init__(self, store: InMemoryStore, outbox: OutboxPort) -> None:
        self._store = store
        self._outbox = outbox
        self._lock = asyncio.Lock()
        self._store_snapshot: StoreSnapshot | None = None

    async def __aenter__(self) -> Self:
        await self._lock.acquire()
        self._store_snapshot = self._store.snapshot()
        await self._outbox.begin()
        return self

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if exc_type is not None:
            if self._store_snapshot is not None:
                self._store.restore(self._store_snapshot)
            await self._outbox.rollback()
        else:
            await self._outbox.commit()
        self._lock.release()
