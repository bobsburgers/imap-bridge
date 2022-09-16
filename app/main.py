import asyncio
import os
import sys

from app.service.email_checker import EMailChecker

_local_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(_local_dir))

from app.service.dispatcher import EventDispatcher
from app.service.local_ip import get_local_ip
from tracardi.domain.event_source import EventSource

import logging

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import app.config as config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

application = FastAPI(
        title="Tracardi IMAP Bridge",
        description="TRACARDI open-source_id customer data platform",
        version="0.7.2-dev",
        contact={
            "name": "Risto Kowaczewski, Ben Ullrich",
            "url": "http://github.com/tracardi/imap-bridge",
            "email": "office@tracardi.com",
        },
)

application.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
)


def run_imap_bridge():
    async def heartbeat():
        e = EMailChecker(host=config.imap.host, port=config.imap.port,
                         user=config.imap.user, password=config.imap.password,
                         mailbox=config.imap.mailbox)
        await e.start()
        await e.logout()
    asyncio.create_task(heartbeat())


@application.on_event("startup")
async def app_starts():
    dispatcher = EventDispatcher(type=config.bridge.type)
    event_source = EventSource(
            id=config.tracardi.source_id,
            type='imap',
            name="IMAP Bridge",
            description=f"IMAP Bridge at {get_local_ip()}",
            tags=['imap', 'bridge'],
            transitional=False,
            locked=True,
            groups=["Bridge"],
            manual="""# Bridge description
        
IMAP Bridge runs a imap worker in order to retrieve e-mails and push every new e-mail to Tracardi. 

# Registration

This event source is automatically registered when bridge starts. 
"""
    )
    # result = await dispatcher.register_source(event_source)
    # logger.info(f"IMAP Bridge registered with id {config.tracardi.source_id} and result {result}")
    run_imap_bridge()


@application.on_event("shutdown")
async def app_shutdown():
    dispatcher = EventDispatcher(type=config.bridge.type)
    result = await dispatcher.unregister_source(config.tracardi.source_id)
    logger.info(f"IMAP Bridge unregistered with id {config.tracardi.source_id} and result {result}")


# if not config.imap.is_configured():
#     raise ConnectionError("MQTT Server is not configured.")
#
# if not config.tracardi.is_configured():
#     raise ConnectionError("TRACARDI is not configured.")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run("app.main:application", host="0.0.0.0", port=10002, log_level="info")
