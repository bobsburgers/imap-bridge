import json
import logging
import socket

from app.service.tracardi_api_client import TracardiApiClient
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

    def __init__(self, api_client: TracardiApiClient, event_transport="track"):
        if event_transport not in ['track', 'api']:
            raise ValueError("EVENT_TRANSPORT invalid value. Possible values [track, api]")
        self.event_transport = event_transport
        self.api_client = api_client

    @staticmethod
    async def connect() -> 'EventDispatcher':
        api_client = TracardiApiClient(config.tracardi.api_host)
        await api_client.set_credentials(config.tracardi.username, config.tracardi.password)
        return EventDispatcher(api_client, config.bridge.event_transport)

    @staticmethod
    def _local_ip():
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)

    async def register_source(self, event_source: EventSource):
        if self.event_transport == 'track':
            return await save_source(event_source)
        elif self.event_transport == 'api':
            endpoint = "/event-source"

            payload = json.loads(json.dumps(event_source.dict(), default=str))
            response, json_response, _ = await self.api_client.post(endpoint, json=payload)
            logger.info("TRACARDI: response: status {},  {}".format(response.status, response.reason))

            if response.status == 401:
                raise ConnectionError(f"Can not connect to TRACARDI. Reason: {response.reason}")

            return response

    async def unregister_source(self, source_id):
        if self.event_transport == 'track':
            return await storage.driver.event_source.delete(source_id)
        elif self.event_transport == 'api':
            endpoint = f"/event-source/{source_id}"
            response, json_response, _ = await self.api_client.delete(endpoint)

            if response.status != 200:
                raise ConnectionError(f"Could not unregister source. Reason: {response.reason}")

            logger.info("TRACARDI: response: status {},  {}".format(response.status, response.reason))
            return response

    async def dispatch_track(self, event_type: str, payload: dict):

        try:

            tracker_payload = TrackerPayload(
                source=Entity(id=config.tracardi.source_id),
                session=None,
                metadata=EventPayloadMetadata(time=Time()),
                profile=None,
                context={},
                properties={},
                events=[
                    EventPayload(type=event_type, properties=payload)
                ],
                options={"saveSession": False}
            )

            return await synchronized_event_tracking(tracker_payload, self._local_ip(), profile_less=True,
                                                     allowed_bridges=['imap'])
        except Exception as e:
            logger.error(str(e))

    async def dispatch_vi_api(self, event_type: str, payload: dict):
        payload = payload
        if config.tracardi.event_type is None:
            endpoint = f"/collect/{event_type}/{config.tracardi.source_id}"
        else:
            endpoint = f"/collect/{config.tracardi.event_type}/{config.tracardi.source_id}"

        response, _, data = await self.api_client.post(endpoint, json=payload)
        logger.info("TRACARDI: response: status {},  {}".format(response.status, data))

    async def dispatch(self, event_type: str, payload: dict):
        if self.event_transport == 'track':
            await self.dispatch_track(event_type, payload)
        elif self.event_transport == 'api':
            await self.dispatch_vi_api(event_type, payload)
        else:
            raise ValueError("Unknown dispatcher type.")
