import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager


class ReadWriteLock:
    def __init__(self) -> None:
        self._readers = 0
        self._writer = False
        self._lock = asyncio.Lock()
        self._read_ready = asyncio.Condition(self._lock)

    @asynccontextmanager
    async def read_lock(self) -> AsyncIterator[None]:
        async with self._lock:
            while self._writer:
                await self._read_ready.wait()
            self._readers += 1
        try:
            yield
        finally:
            async with self._lock:
                self._readers -= 1
                if self._readers == 0:
                    self._read_ready.notify_all()

    @asynccontextmanager
    async def write_lock(self) -> AsyncIterator[None]:
        async with self._lock:
            while self._writer:
                await self._read_ready.wait()
            self._writer = True
            while self._readers > 0:
                await self._read_ready.wait()
        try:
            yield
        finally:
            async with self._lock:
                self._writer = False
                self._read_ready.notify_all()


class KeyedLockRegistry:
    def __init__(self) -> None:
        self._locks: dict[tuple[str, str], asyncio.Lock] = {}
        self._lock = asyncio.Lock()

    async def get_lock(self, operation: str, key: str) -> asyncio.Lock:
        async with self._lock:
            return self._locks.setdefault((operation, key), asyncio.Lock())
