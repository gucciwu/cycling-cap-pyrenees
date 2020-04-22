import abc

from message.models import Message, MESSAGE_BACKEND_UNKNOWN, MESSAGE_BACKEND_SMS, MESSAGE_BACKEND_EMAIL


class BaseBackend(metaclass=abc.ABCMeta):

    def __init__(self, backend_type=MESSAGE_BACKEND_UNKNOWN):
        self._type = backend_type

    def get_type(self):
        return self._type

    @staticmethod
    @abc.abstractmethod
    def send(message: Message):
        pass


class BaseSmsBackend(BaseBackend):

    def __init__(self):
        super().__init__(MESSAGE_BACKEND_SMS)

    @staticmethod
    @abc.abstractmethod
    def send(message: Message):
        pass


class BaseEmailBackend(BaseBackend):

    def __init__(self):
        super().__init__(MESSAGE_BACKEND_EMAIL)

    @staticmethod
    @abc.abstractmethod
    def send(message: Message):
        pass
