import asyncio
import logging

from tracardi.domain.event_source import EventSource

from app import config
from app.bridge.email_checker import EMailChecker
from app.service.local_ip import get_local_ip
from app.service.main_loop import MainLoop

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def run_bridge(_shut_down):
    """
    This is the function to run the bridge loop
    _shut_down: Will be called on the shut-down
    """

    checker = await EMailChecker.connect()

    try:
        while checker.run:
            await checker.fetch_all_unseen()
            await checker.wait_for_new_message()
    except asyncio.CancelledError:
        logger.info("Canceling task.")
        await _shut_down()
        #todo logout does not work
        # await checker.logout()

"""
Event source to open for this bridge. Use config.bridge.event_transport = track whenever possible.
It gives more protection on the event source. If you use config.bridge.event_transport = api then regular
REST API is used. 
"""
bridge_type = 'rest' if config.bridge.event_transport == 'api' else 'imap'
event_source = EventSource(
    id=config.tracardi.source_id,
    type=bridge_type,
    name="IMAP Bridge",
    description=f"IMAP Bridge at {get_local_ip()}",
    tags=[bridge_type, 'bridge'],
    transitional=False,
    locked=True,
    groups=["Bridge"],
    manual="# Bridge description\n\nIMAP Bridge runs a imap worker in order to retrieve e-mails and push every new "
           "e-mail to Tracardi.\n\n# Registration\n\nThis event source is automatically registered when bridge "
           "starts."
)

try:
    MainLoop(run_bridge, event_source)
except KeyboardInterrupt:
    print("Received exit, exiting")
