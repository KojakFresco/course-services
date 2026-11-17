from dataclasses import dataclass

CHECKS_COMMAND_TOPIC = "checks.command"
CHECKS_EVENTS_TOPIC = "checks.events"
SIMILARITY_COMMAND_TOPIC = "similarity.command"
SIMILARITY_EVENTS_TOPIC = "similarity.events"


@dataclass(frozen=True)
class PublishedMessage:
    topic: str
    payload: dict[str, object]


class MockKafkaPublisher:
    """In-memory Kafka adapter used by tests and the lab architecture."""

    def __init__(self) -> None:
        self.messages: list[PublishedMessage] = []

    async def publish(self, topic: str, payload: dict[str, object]) -> None:
        self.messages.append(PublishedMessage(topic=topic, payload=payload))
