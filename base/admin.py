from django.contrib import admin

from base.models import get_user_from_request
from entry.settings import ADMIN_SITE
from utils.date import now


class BaseModelAdmin(admin.ModelAdmin):
    list_display = ('pyr_guid', 'created_time', 'created_by',
                    'modified_time', 'modified_by')
    readonly_fields = ('created_time', 'created_by',
                       'modified_time', 'modified_by', 'owner', 'deleted', 'pyr_guid')
    save_on_top = True
    search_fields = ('modified_by__username', 'created_by__username', 'owner__username', 'pyr_guid')
    list_filter = ('deleted',)

    def get_queryset(self, request, only_owner=True):
        qs = super().get_queryset(request)
        if request.user.is_superuser or not only_owner:
            return qs
        return qs.filter(owner=request.user)

    def extend_list(self, extends=None):
        if extends is not None:
            self.list_display = ('__str__',) + \
                                extends + \
                                ('created_time', 'created_by',
                                 'modified_time', 'modified_by', 'deleted')

    def save_model(self, request, obj, form, change):
        user = get_user_from_request(request)
        obj.modified_by = user
        obj.modified_time = now()

        if not change:
            obj.owner = user
            obj.created_by = user
            obj.created_time = now()

        super().save_model(request, obj, form, change)


admin.site.site_header = ADMIN_SITE['site_header']
admin.site.site_title = ADMIN_SITE['site_title']
