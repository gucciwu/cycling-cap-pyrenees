import base64
import hashlib

from Crypto.Cipher import AES
from entry.settings import SECRET_KEY

aes = AES.new(str.encode(SECRET_KEY), AES.MODE_ECB)


def add_to_16(s):
    while len(s) % 16 != 0:
        s += '\0'
    return str.encode(s)


def encrypt(text):
    return str(base64.encodebytes(aes.encrypt(add_to_16(text))), encoding='utf8').replace('\n', '')


def decrypt(text):
    return str(aes.decrypt(base64.decodebytes(bytes(text, encoding='utf8'))).rstrip(b'\0').decode("utf8"))


def md5(text):
    m = hashlib.md5()
    m.update(text)
    return m.hexdigest()


def mask(text):
    if len(text) < 3:
        return '*' * len(text)

    # maybe mobile
    if len(text) == 11:
        return text[0:3] + ('*' * 4) + text[8:]

    # maybe id card no
    if len(text) == 18:
        return text[0:2] + ('*' * 12) + text[14:]

    return text[0] + ('*' * (len(text)-2)) + text[-1]
