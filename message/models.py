import logging
from string import Template

from django.contrib.auth.models import User
from django.db import models

from base.models import BaseModel, get_system_user
from entry.settings import DATABASE_TABLE_PREFIX
from utils.date import now

from .exceptions import MessageException

logger = logging.getLogger(__name__)

MESSAGE_BACKEND_UNKNOWN = 0
MESSAGE_BACKEND_SMS = 1
MESSAGE_BACKEND_EMAIL = 2
MESSAGE_BACKEND_WECHAT = 3
MESSAGE_BACKEND_LETTER = 4
MESSAGE_BACKEND_NOTICE = 5

MESSAGE_BACKEND_LIST = [
    (MESSAGE_BACKEND_UNKNOWN, 'Unknown'),
    (MESSAGE_BACKEND_SMS, 'SMS'),
    (MESSAGE_BACKEND_EMAIL, 'Email'),
    (MESSAGE_BACKEND_WECHAT, 'WeChat'),
    (MESSAGE_BACKEND_LETTER, 'Letter'),
    (MESSAGE_BACKEND_NOTICE, 'Notice')]

MESSAGE_STATUS_DRAFT = -1
MESSAGE_STATUS_READ = 0
MESSAGE_STATUS_OUTSTANDING = 1
MESSAGE_STATUS_WIP = 2
MESSAGE_STATUS_SUCCESS = 3
MESSAGE_STATUS_FAILED = 4
MESSAGE_STATUS_CANCELLED = 5
MESSAGE_STATUS_LIST = [(MESSAGE_STATUS_OUTSTANDING, 'Outstanding'),
                       (MESSAGE_STATUS_WIP, 'WIP'),
                       (MESSAGE_STATUS_SUCCESS, 'Success'),
                       (MESSAGE_STATUS_FAILED, 'Failed'),
                       (MESSAGE_STATUS_CANCELLED, 'Cancelled'),
                       (MESSAGE_STATUS_READ, 'Read')]


class Message(BaseModel):

    sender = models.ForeignKey(User, limit_choices_to={'is_active': True},
                               related_name="%(app_label)s_%(class)ss_sender_related",
                               related_query_name="%(app_label)s_%(class)ss_sender",
                               on_delete=models.DO_NOTHING)
    receiver = models.ForeignKey(User, limit_choices_to={'is_active': True},
                                 related_name="%(app_label)s_%(class)ss_receiver_related",
                                 related_query_name="%(app_label)s_%(class)ss_receiver",
                                 on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=40)
    content = models.TextField()
    wrote_time = models.DateTimeField(verbose_name="Wrote At", auto_now_add=True)
    status = models.IntegerField(choices=MESSAGE_STATUS_LIST, default=MESSAGE_STATUS_DRAFT)

    class Meta:
        db_table = DATABASE_TABLE_PREFIX + 'message'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sender = get_system_user()
        self.set_user(self.sender)

    def __str__(self):
        return self.title

    def parse_template(self, template, keywords=None):
        if keywords is None:
            keywords = {}
        if template is not None:
            title_template = Template(template.get('title', ""))
            content_template = Template(template.get('content', ""))
            self.title = title_template.substitute(keywords)
            self.content = content_template.substitute(keywords)
        return self


class Messager(BaseModel):
    message = models.ForeignKey(Message, related_name="%(app_label)s_%(class)ss_message_related",
                                related_query_name="%(app_label)s_%(class)ss_message",
                                on_delete=models.DO_NOTHING,
                                verbose_name='Message')
    backend_type = models.IntegerField(choices=MESSAGE_BACKEND_LIST, default=MESSAGE_BACKEND_UNKNOWN)
    send_time = models.DateTimeField(null=True, blank=True)
    arrive_time = models.DateTimeField(null=True, blank=True)
    read_time = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(choices=MESSAGE_STATUS_LIST, default=MESSAGE_STATUS_OUTSTANDING)
    memo = models.TextField(null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_user(get_system_user())

    def __str__(self):
        return self.message.title

    def set_backend(self, backend):
        self._backend = backend()
        self.backend_type = self._backend.get_type()
        return self

    def send(self):
        self.send_time = now()
        try:
            result = self._backend.send(self.message)
            self.memo = result
            self.status = MESSAGE_STATUS_SUCCESS
            self.message.status = MESSAGE_STATUS_SUCCESS
        except MessageException as err:
            self.memo = err
            self.status = MESSAGE_STATUS_FAILED
            self.message.status = MESSAGE_STATUS_FAILED
            logger.warning(err)
        finally:
            pass
            self.message.save()
            self.save()

    class Meta:
        db_table = DATABASE_TABLE_PREFIX + 'messager'
