from rest_framework import viewsets, mixins, status
from rest_framework.views import APIView

from base.http import AlpsRestResponse
from base.models import get_user_from_request
from counter.models import Counter
from counter.services import count
from utils.action_history import log_deletion, log_change, log_addition


class BaseViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return AlpsRestResponse.fail(status=status.HTTP_403_FORBIDDEN)
        user = get_user_from_request(request)
        message = '%s soft deleted %s' % (user.username, str(instance))
        log_deletion(user, instance, message)
        self.perform_destroy(instance)
        return AlpsRestResponse.success(status=status.HTTP_202_ACCEPTED)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        instance = serializer.instance
        user = get_user_from_request(request)
        message = '%s created %s' % (user.username, str(instance))
        log_addition(user, instance, message)
        return AlpsRestResponse.success(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get(self.lookup_field, None)

        if pk is None:
            return AlpsRestResponse.fail(status=status.HTTP_404_NOT_FOUND)
        elif pk.isdigit():
            # query by ID
            instance = self.get_object()
        else:
            # query by pyrenees GUID
            model = self.serializer_class.Meta.model
            try:
                instance = model.objects.get(pyr_guid=pk)
            except model.DoesNotExist as err:
                return AlpsRestResponse.fail(status=status.HTTP_404_NOT_FOUND)

        if instance is None:
            return AlpsRestResponse.fail(status=status.HTTP_404_NOT_FOUND)

        # count
        views = count(instance, Counter.TYPE_VIEW)
        serializer = self.get_serializer(instance)
        return AlpsRestResponse.success(serializer.data, extra={'views': views})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        user = get_user_from_request(request)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        message = '%s changed %s' % (user.username, str(instance))
        log_change(user, instance, message)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return AlpsRestResponse.success(serializer.data)


class BaseAPIView(APIView):
    pass
