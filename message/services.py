import logging

from .backends.email import DjangoEmailBackend
from .models import Message, Messager
from .templates import REGISTER_VERIFY_CODE
from utils.data import guid

logger = logging.getLogger(__name__)


def send_active_mail(user):
    if not user.email:
        return

    message = Message().parse_template(template=REGISTER_VERIFY_CODE,
                                       keywords={'active_code': guid(),
                                                 "email": user.email})
    message.receiver = user
    messager = Messager().set_backend(DjangoEmailBackend)
    messager.message = message
    messager.send()
    logger.info('Active email has sent to %s' % user.username)
