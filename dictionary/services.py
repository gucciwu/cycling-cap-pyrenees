from .models import Dictionary
import logging

logger = logging.getLogger(__name__)


def get_value(entry: str, key: str):
    ret = Dictionary.objects.filter(entry=entry).filter(key=str)
    if len(ret) > 0:
        return ret[0]
    else:
        logger.warning('system dictionary not found! %s/%s' % (entry, key))

    return ""
