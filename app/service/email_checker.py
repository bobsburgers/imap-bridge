import asyncio
import ssl
import email
import aioimaplib as aioimaplib
from aioimaplib import STOP_WAIT_SERVER_PUSH

from app import config
from app.service.dispatcher import EventDispatcher

get_these = ('Content-Type', 'From', 'To', 'Cc', 'Bcc', 'Date', 'Subject')


class EMailChecker:
    def __init__(self, host: str, port: int, user: str, password: str, mailbox: str):
        self.password = password
        self.user = user
        self.port = port
        self.host = host
        self.run = True
        self.client = None  # type: aioimaplib.IMAP4 or aioimaplib.IMAP4_SSL
        self.mailbox = mailbox
        self.dispatcher = EventDispatcher(event_type=config.bridge.event_type)
    
    async def get_client_logged_in(self) -> aioimaplib.IMAP4 or aioimaplib.IMAP4_SSL:
        try:
            self.client = aioimaplib.IMAP4_SSL(host=self.host, port=self.port)
        except ssl.SSLError:
            self.client = aioimaplib.IMAP4(host=self.host, port=self.port)
        await self.client.wait_hello_from_server()
        await self.client.login(self.user, self.password)
        await self.client.select(self.mailbox)
        return self.client
    
    async def logout(self):
        if self.client:
            await self.client.logout()
    
    async def fetch(self, search: str = 'Unseen') -> [{}, ]:
        ids = await self.fetch_ids(search)
        emails = []
        for _id in ids[0].split()[::-1]:
            _id = '%d' % int(_id)
            email = await self.client.uid('fetch', _id, 'BODY.PEEK[]')
            emails.append(email)
        # emails += self.make_dict_from_email(data)
        return emails
    
    @staticmethod
    async def make_dict_from_email(data):
        email = {
            'headers': data[0][1],
            'from': data[0][1],
            'to': data[0][1],
            'subject': data[0][1],
            'body': data[0][1],
            'rawbody': data[0][1],
        }
        return email
    
    async def fetch_ids(self, search: str) -> [bytes, ]:
        # await self.client.select(self.mailbox)
        result, data = await self.client.search(search)
        assert result == 'OK'
        return data
    
    def stop(self):
        self.run = False
    
    async def start(self):
        self.client = await self.get_client_logged_in()  # type: aioimaplib.IMAP4 or aioimaplib.IMAP4_SSL
        unreads = await self.fetch(search='Unseen')
        for unread in unreads:
            s = self.process_to_dict(unread)
            r = await self.dispatcher.dispatch(config.bridge.event_type, s)
            pass
        while self.run:
            await self.wait_for_new_message()
        await self.logout()
        return
    
    @staticmethod
    def process_to_dict(response) -> dict:
        if response.result == 'OK':
            msg = email.message_from_bytes(response[1][1])
            
            email_dict = {g: msg[g] for g in get_these if msg[g]}
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    cdispo = str(part.get('Content-Disposition'))
                    
                    if ctype == 'text/plain' and 'attachment' not in cdispo:
                        email_dict['body'] = part.get_payload(decode=False)  # decode
                        break
            else:
                email_dict['body'] = msg.get_payload(decode=False)
            return email_dict
    
    async def wait_for_new_message(self, ):
        await self.client.select(self.mailbox)
        idle = await self.client.idle_start(timeout=10)
        while self.run and self.client.has_pending_idle():
            msg = await self.client.wait_server_push()
            print(msg)
            if msg == STOP_WAIT_SERVER_PUSH:
                self.client.idle_done()
                await asyncio.wait_for(idle, 1)
            else:
                msg = self.process_to_dict(msg)
                await self.dispatcher.dispatch(config.bridge.event_type, msg)
        # await self.client.logout()
