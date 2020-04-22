import logging

from counter.models import Counter

logger = logging.getLogger(__name__)


def count(obj, counter_type=Counter.TYPE_VIEW):
    if not hasattr(obj, 'countable') or not hasattr(obj, 'pyr_guid'):
        return 0
    if not obj.countable or not obj.pyr_guid:
        return 0

    result = Counter.objects.filter(guid=obj.pyr_guid).filter(counter_type=counter_type)
    result_count = len(result)
    counter = None

    if result_count == 0:
        counter = Counter()
        counter.counter_type = counter_type
        counter.guid = obj.pyr_guid
        counter.value = 0
    elif result_count == 1:
        counter = result[0]
    elif result_count > 1:
        logger.warning('duplicate counter found by GUID %s and type %s' % (obj.pyr_guid, counter_type))
        counter = result[0]

    counter.value = counter.value + 1
    counter.save()
    return counter.value
