import asyncio
import ssl

import aioimaplib as aioimaplib
from aioimaplib import STOP_WAIT_SERVER_PUSH

ID_HEADER_SET = {'Content-Type', 'From', 'To', 'Cc', 'Bcc', 'Date', 'Subject',
                 'Message-ID', 'In-Reply-To', 'References'}


class EMailChecker:
	def __init__(self, host: str, port: int, user: str, password: str, mailbox: str):
		self.password = password
		self.user = user
		self.port = port
		self.host = host
		self.run = True
		self.client = None  # type: aioimaplib.IMAP4 or aioimaplib.IMAP4_SSL
		self.mailbox = mailbox
	
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
	
	async def fetch_unread(self, ):
		unread = await self.fetch(search='Unseen')
		# todo prep fetched emails
		return unread
	
	async def fetch(self, search: str = 'Unseen') -> [{}, ]:
		# await self.client.select(self.mailbox)
		ids = await self.fetch_ids(search)
		emails = []
		for _id in ids[0].split()[::-1]:
			# data = await self.client.fetch(f'{str(_id)}:{str(int(_id)+1)}', "(RFC822)")
			# dataa = await self.client.uid('fetch', str(_id), "(RFC822)")
			_id = int(_id)
			emails += await self.client.uid('fetch', '%d' % _id,
			                                '(UID FLAGS BODY.PEEK[HEADER.FIELDS (%s)])' % ' '.join(ID_HEADER_SET))
			pass
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
		await self.fetch_unread()
		while self.run:
			await self.wait_for_new_message()
		await self.logout()
		return
	
	async def wait_for_new_message(self, ):
		await self.client.select(self.mailbox)
		idle = await self.client.idle_start(timeout=10)
		while self.run and self.client.has_pending_idle():
			msg = await self.client.wait_server_push()
			print(msg)
			if msg == STOP_WAIT_SERVER_PUSH:
				self.client.idle_done()
				await asyncio.wait_for(idle, 1)

# email = EMailChecker(
#         host='imap.google.com',
#         port=993,
#         user='',
#         password=''
# )

# check for new mail every minute
# print(email.fetch())
