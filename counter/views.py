import logging

from base.http import AlpsRestResponse
from counter.models import Counter

logger = logging.getLogger(__name__)


def count(request):
    guid = request.DATA.get('guid', None)
    counter_type = request.DATA.get('type', Counter.TYPE_VIEW)

    if guid is None:
        return AlpsRestResponse.success({'count': 0})

    result = Counter.objects.filter(guid=guid).filter(counter_type=counter_type)
    result_count = len(result)
    if result_count == 0:
        return AlpsRestResponse.success({'count': 0})
    elif result_count == 1:
        return AlpsRestResponse.success({'count': result[0].value})
    elif result_count > 1:
        logger.warning('duplicate counter found of GUID %s and type %s!' % (guid, counter_type))
        return AlpsRestResponse.success({'count': result[0].value})

