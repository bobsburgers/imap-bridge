import imaplib


class EMailChecker:
    def __init__(self, server, port, user, password,):
        self.password = password
        self.user = user
        self.port = port
        self.server = server
        self.client = imaplib.IMAP4_SSL(self.server, self.port)
        self.client.login(self.user, self.password)

    def fetch(self):
        self.client.select()
        return self.client.search(None, 'UnSeen')


email = EMailChecker(
    server='imap.google.com',
    port=993,
    user='',
    password=''
)

# check for new mail every minute
print(email.fetch())
