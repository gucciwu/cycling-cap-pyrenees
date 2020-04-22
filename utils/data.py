import datetime
import json
from collections import namedtuple
from decimal import Decimal
import uuid
import re

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from entry.settings import PYRENEES_CLUSTER
from utils.date import now


def clean_values(data, instance):
    ret = {}
    for key in data.keys():
        if hasattr(instance, key):
            instance_value = getattr(instance, key)
            if isinstance(instance_value, Decimal):
                if data[key] == '':
                    continue

        ret[key] = data[key]

    return ret


def clean_sql_table_column(sql_str):
    bad_characters = ('%', ' ', '@', '/')
    for character in bad_characters:
        sql_str = sql_str.replace(character, '')
    return sql_str


def named_tuple_fetch_all(cursor, label='Result'):
    """Return all rows from a cursor as a namedtuple"""
    desc = cursor.description
    nt_result = namedtuple(label, [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def guid():
    ret = '%s-%s-%s-%s' % (now().strftime('%Y%m%d%H%M%S%f'),
                           PYRENEES_CLUSTER['GROUP_NAME'], PYRENEES_CLUSTER['NODE_NAME'],
                           str(uuid.uuid1()).split('-')[0])
    return str(ret)


def format_mobile_no(no):
    """
    format mobile no to e.164
    @params: mobile no
    """
    no += ""  # maybe pass a int value

    if len(no) == 11:
        no = "+86" + no

    return no


def is_mobile(text):
    return re.match(r"^1[35678]\d{9}$", text)


def is_email(text):
    try:
        validate_email(text)
        return True
    except ValidationError as err:
        return False


def try_to_number(value):
    if isinstance(value, float) or isinstance(value, int):
        return value
    org = value
    if isinstance(value, str) and value != '':
        if value.isdecimal():
            return int(org)
        elif value.replace('.', '').isdecimal():
            return float(org)

    return org


def has(key, obj):
    if isinstance(obj, list):
        return key in list
    if isinstance(obj, dict):
        return key in list(obj.keys())
    return False


class JSONEncoder(json.JSONEncoder):
    """convert ObjectId and datetime to string"""

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return datetime.datetime.strftime(o, '%Y-%m-%d %H:%M:%S')
        if isinstance(o, datetime.time):
            return datetime.time.strftime(o, '%H:%M:%S')
        elif isinstance(o, bytes):
            return str(o)
        return json.JSONEncoder.default(self, o)
