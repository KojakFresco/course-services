import asyncio

from course_service.application.ports import (
    OutboxMessage,
    OutboxPort,
)


class InMemoryOutbox(OutboxPort):
    def __init__(self) -> None:
        self._messages: list[OutboxMessage] = []
        self._lock = asyncio.Lock()
        self._next_id = 1
        self._transaction_messages: list[OutboxMessage] | None = None

    async def begin(self) -> None:
        async with self._lock:
            if self._transaction_messages is not None:
                raise RuntimeError("Outbox transaction already active")
            self._transaction_messages = []

    async def commit(self) -> None:
        async with self._lock:
            if self._transaction_messages is None:
                raise RuntimeError("Outbox transaction is not active")
            self._messages.extend(self._transaction_messages)
            self._transaction_messages = None

    async def rollback(self) -> None:
        async with self._lock:
            if self._transaction_messages is None:
                raise RuntimeError("Outbox transaction is not active")
            self._transaction_messages = None

    async def add(self, topic: str, payload: dict[str, object]) -> None:
        async with self._lock:
            message = OutboxMessage(self._next_id, topic, payload)
            if self._transaction_messages is not None:
                self._transaction_messages.append(message)
            else:
                self._messages.append(message)
            self._next_id += 1

    async def pending(self) -> list[OutboxMessage]:
        async with self._lock:
            return [message for message in self._messages if not message.published]

    async def mark_published(self, message_id: int) -> None:
        async with self._lock:
            self._messages = [
                OutboxMessage(message.id, message.topic, message.payload, True)
                if message.id == message_id
                else message
                for message in self._messages
            ]
