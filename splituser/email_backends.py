from aiosmtpd.handlers import Message
from aiosmtpd.smtp import SMTP as SMTPServer
from django.core.mail.backends.smtp import EmailBackend
from email.mime.text import MIMEText

class AioSMTPServer(SMTPServer):
    async def smtp_DATA(self, arg):
        self.received_data = []
        await super().smtp_DATA(arg)

    async def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        message = MIMEText(''.join(data), 'plain')
        message['From'] = mailfrom
        message['To'] = ', '.join(rcpttos)
        message['Subject'] = 'Test Email'

class AioEmailBackend(EmailBackend):
    async def send_messages(self, email_messages):
        for email in email_messages:
            await self._send(email)

    async def _send(self, email_message):
        handler = Message(AioSMTPServer())
        await handler._call_hook('rcpt')
        await handler._call_hook('data')
