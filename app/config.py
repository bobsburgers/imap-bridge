import logging
import os
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv(r'.env')


def _get_logging_level(level: str) -> int:
    level = level.upper()
    if level == 'DEBUG':
        return logging.DEBUG
    if level == 'INFO':
        return logging.INFO
    if level == 'WARNING' or level == "WARN":
        return logging.WARNING
    if level == 'ERROR':
        return logging.ERROR

    return logging.WARNING


class BridgeConfig:
    def __init__(self, env):
        self.event_transport = env['EVENT_TRANSPORT'] if 'EVENT_TRANSPORT' in env else 'track'
        self.wait = 1


class TracardiConfig:
    def __init__(self, env):
        self.api_host = env['TRACARDI_API_HOST'] if 'TRACARDI_API_HOST' in env else None
        self.source_id = env['TRACARDI_SOURCE_ID'] if 'TRACARDI_SOURCE_ID' in env else str(uuid4())
        self.event_type = env['TRACARDI_EVENT_TYPE'] if 'TRACARDI_EVENT_TYPE' in env else None
        self.username = env['TRACARDI_USERNAME'] if 'TRACARDI_USERNAME' in env else ""
        self.password = env['TRACARDI_PASSWORD'] if 'TRACARDI_PASSWORD' in env else ""

    def is_configured(self):
        return self.api_host is not None


class IMAPConfig:
    def __init__(self, env):
        self.host = env['IMAP_HOST'] if 'IMAP_HOST' in env else 'localhost'
        self.port = int(env['IMAP_PORT']) if 'IMAP_PORT' in env else 1883
        self.user = env['IMAP_USERNAME'] if 'IMAP_USERNAME' in env else None
        self.password = env['IMAP_PASSWORD'] if 'IMAP_PASSWORD' in env else None
        self.mailbox = env['IMAP_MAILBOX'] if 'IMAP_MAILBOX' in env else 'INBOX'

    def is_configured(self):
        return self.host is not None and self.user is not None and self.password is not None


imap = IMAPConfig(os.environ)
tracardi = TracardiConfig(os.environ)
bridge = BridgeConfig(os.environ)
