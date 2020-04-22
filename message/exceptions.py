from smtplib import SMTPException


class MessageException(Exception):
    pass


class EmailException(SMTPException, MessageException):
    pass
