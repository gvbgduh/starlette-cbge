"""
Additional test client - `AsyncTestClient`.

TODO: WIP to move it from `requests-async` to `httpx`.
"""
import asyncio

from types import TracebackType
from typing import Type

from requests_async import ASGISession


class AsyncTestClient(ASGISession):
    async def lifespan(self) -> None:
        scope = {"type": "lifespan"}
        try:
            await self.app(scope, self.receive_queue.get, self.send_queue.put)
        finally:
            await self.send_queue.put(None)

    async def wait_startup(self) -> None:
        await self.receive_queue.put({"type": "lifespan.startup"})
        message = await self.send_queue.get()
        if message is None:
            self.task.result()
        assert message["type"] == "lifespan.startup.complete"

    async def wait_shutdown(self) -> None:
        await self.receive_queue.put({"type": "lifespan.shutdown"})
        message = await self.send_queue.get()
        if message is None:
            self.task.result()
        assert message["type"] == "lifespan.shutdown.complete"
        await self.task

    async def __aenter__(self) -> ASGISession:
        loop = asyncio.get_event_loop()
        self.send_queue = asyncio.Queue()  # type: asyncio.Queue
        self.receive_queue = asyncio.Queue()  # type: asyncio.Queue
        self.task = loop.create_task(self.lifespan())
        await self.wait_startup()
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] = None,
        exc_value: BaseException = None,
        traceback: TracebackType = None,
    ) -> None:
        await self.wait_shutdown()
