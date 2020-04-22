from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from base.http import AlpsRestResponse
from .models import Dictionary
from base.views import BaseViewSet
from .serializers import DictionarySerializer
from .services import get_value


class DictionaryViewSet(BaseViewSet):
    """
    API endpoint that allows dictionary entries to be viewed or edited.
    """
    queryset = Dictionary.objects.all().order_by('modified_time')
    serializer_class = DictionarySerializer

    @action(detail=False, methods=['GET'], permission_classes=(AllowAny,))
    def get_value(self, request, entry, key):
        value = get_value(entry.upper(), key.upper())
        return AlpsRestResponse.success(value)
