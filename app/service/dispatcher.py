import json
import logging
import socket

import aiohttp
from tracardi.domain.entity import Entity
from tracardi.domain.event_metadata import EventPayloadMetadata
from tracardi.domain.event_source import EventSource
from tracardi.domain.payload.event_payload import EventPayload
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.time import Time
from tracardi.service.event_source_manager import save_source
from tracardi.service.storage.driver import storage
from tracardi.service.tracker import synchronized_event_tracking

from app import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EventDispatcher:

    def __init__(self, event_type="track"):
        self.event_type = event_type

    @staticmethod
    def _local_ip():
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)

    async def register_source(self, event_source: EventSource):
        if self.event_type == 'track':
            return await save_source(event_source)
        elif self.event_type == 'api':
            async with aiohttp.ClientSession() as session:
                url = f"{config.tracardi.api_host}/event-source"

                # todo authenticate first

                payload = json.dumps(event_source.dict(), default=str)
                async with session.post(url, json=payload) as response:
                    logger.info("TRACARDI: response: status {},  {}".format(response.status, await response.text()))
                    return response

    async def unregister_source(self, source_id):
        if self.event_type == 'track':
            return await storage.driver.event_source.delete(source_id)
        elif self.event_type == 'api':
            async with aiohttp.ClientSession() as session:

                # todo authenticate first

                url = f"{config.tracardi.api_host}/event-source"
                async with session.delete(url) as response:
                    logger.info("TRACARDI: response: status {},  {}".format(response.status, await response.text()))
                    return response

    async def dispatch_track(self, event_type, properties):

        try:

            tracker_payload = TrackerPayload(
                source=Entity(id=config.tracardi.source_id),
                session=None,
                metadata=EventPayloadMetadata(time=Time()),
                profile=None,
                context={},
                properties={},
                events=[
                    EventPayload(type=event_type, properties=properties)
                ],
                options={"saveSession": False}
            )

            return await synchronized_event_tracking(tracker_payload, self._local_ip(), profile_less=True,
                                                     allowed_bridges=['imap'])
        except Exception as e:
            logger.error(str(e))

    async def dispatch_vi_api(self, event_type, properties):

        async with aiohttp.ClientSession() as session:

            if config.tracardi.event_type is None:
                url = f"{config.tracardi.api_host}/collect/{event_type}/{config.tracardi.source_id}"
                payload = properties
            else:
                url = f"{config.tracardi.api_host}/collect/{config.tracardi.event_type}/{config.tracardi.source_id}"
                payload = properties
            async with session.post(url, json=payload) as response:
                logger.info("TRACARDI: response: status {},  {}".format(response.status, await response.text()))

    async def dispatch(self, topic, payload):
        if self.event_type == 'track':
            await self.dispatch_track(topic, payload)
        elif self.event_type == 'api':
            await self.dispatch_vi_api(topic, payload)
        else:
            raise ValueError("Unknown dispatcher type.")
