from course_service.application.ports import EventPublisherPort, OutboxPort


class OutboxDispatcher:
    def __init__(self, outbox: OutboxPort, publisher: EventPublisherPort) -> None:
        self._outbox = outbox
        self._publisher = publisher

    async def publish_pending(self) -> None:
        for message in await self._outbox.pending():
            await self._publisher.publish(message.topic, message.payload)
            await self._outbox.mark_published(message.id)
