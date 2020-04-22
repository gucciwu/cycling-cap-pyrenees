import logging
from django.core.mail import send_mail
from message.backends.Base import BaseEmailBackend
from entry import settings
from message.exceptions import EmailException
from message.models import Message

logger = logging.getLogger(__name__)


class DjangoEmailBackend(BaseEmailBackend):

    @staticmethod
    def send(message: Message):
        try:
            return send_mail(subject=message.title,
                             from_email=settings.SERVER_EMAIL,
                             recipient_list=[message.receiver.email],
                             message=message.content,
                             html_message=message.content,
                             fail_silently=False)
        except EmailException as err:
            logger.warning(err)
