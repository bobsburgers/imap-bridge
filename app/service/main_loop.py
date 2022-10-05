import asyncio
import logging
import signal

from tracardi.domain.event_source import EventSource

from app import config
from app.service.dispatcher import EventDispatcher

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MainLoop:

    def __init__(self, coro, event_source: EventSource):
        loop = asyncio.get_event_loop()
        self.event_source = event_source
        self.main_task = loop.create_task(self.main(coro))
        for sig in [signal.SIGINT, signal.SIGTERM]:
            loop.add_signal_handler(sig, self.main_task.cancel)
        loop.set_exception_handler(self._exception_handler)
        loop.run_until_complete(self.main_task)

    async def _set_up(self):
        dispatcher = await EventDispatcher.connect()

        await dispatcher.register_source(self.event_source)
        logger.info(f"{self.event_source.name} registered with id {config.tracardi.source_id} as {self.event_source.type.upper()}")

    async def _shut_down(self):
        dispatcher = await EventDispatcher.connect()
        await dispatcher.unregister_source(config.tracardi.source_id)
        logger.info(f"{self.event_source.name} unregistered with id {config.tracardi.source_id}")

    async def main(self, coro):
        await self._set_up()
        await coro(self._shut_down)

    def _exception_handler(self, loop, context):
        loop.default_exception_handler(context)
        self.main_task.cancel()
