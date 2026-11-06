from collections.abc import Awaitable, Callable
from typing import Protocol

import nats

SUBJECT = "zukunftstag.chat"

Handler = Callable[[bytes], Awaitable[None]]


class Bus(Protocol):
    async def start(self) -> None: ...

    async def stop(self) -> None: ...

    async def publish(self, data: bytes) -> None: ...

    def subscribe(self, handler: Handler) -> None: ...


class NatsBus:
    """NATS plays "the internet": everything sent over it can be seen by anyone subscribed."""

    def __init__(self, url: str, subject: str = SUBJECT):
        self._url, self._subject = url, subject
        self._handlers: list[Handler] = []
        self._nc = None

    def subscribe(self, handler: Handler) -> None:
        self._handlers.append(handler)

    async def start(self) -> None:
        self._nc = await nats.connect(self._url, max_reconnect_attempts=-1)

        async def on_msg(msg):
            for h in self._handlers:
                await h(msg.data)

        await self._nc.subscribe(self._subject, cb=on_msg)

    async def stop(self) -> None:
        if self._nc:
            await self._nc.drain()

    async def publish(self, data: bytes) -> None:
        await self._nc.publish(self._subject, data)


class MemoryBus:
    def __init__(self):
        self.published: list[bytes] = []
        self._handlers: list[Handler] = []

    def subscribe(self, handler: Handler) -> None:
        self._handlers.append(handler)

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        pass

    async def publish(self, data: bytes) -> None:
        self.published.append(data)
        for h in self._handlers:
            await h(data)
