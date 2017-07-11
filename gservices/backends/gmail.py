import base64
from email.mime.text import MIMEText

import httplib2
from django.core.mail import EmailMessage
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
from googleapiclient import errors


class GMail(BaseEmailBackend):
    def send_messages(self, email_messages):
        r_http = settings.DELEGATED_CREDENTIALS.authorize(httplib2.Http())

        for m in email_messages:
            message = MIMEText(m.body)
            message['to'] = ','.join(m.to)
            message['from'] = m.from_email
            message['subject'] = m.subject
            settings.GMAIL_SERVICE.users().messages().send(userId='me', body={'raw':  base64.urlsafe_b64encode(message.as_string())}).execute(http=r_http)


# def send_email():
#     m = EmailMessage(subject='Test Email',
#                            body='Test Email',
#                            to=['iandowell7@gmail.com'],
#                            from_email='ian@iandowell.com')
#
#     message = MIMEText(m.body)
#     message['to'] = ','.join(m.to)
#     message['from'] = m.from_email
#     message['subject'] = m.subject
#     r_http = settings.DELEGATED_CREDENTIALS.authorize(httplib2.Http())
#
#     try:
#         message = (settings.GMAIL_SERVICE.users().messages().send(userId='me', body={'raw':  base64.urlsafe_b64encode(message.as_string())})
#                    .execute(http=r_http))
#         print 'Message Id: %s' % message['id']
#         return message
#     except errors.HttpError, error:
#         print 'An error occurred: %s' % error

