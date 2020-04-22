from django.contrib import admin

from base.admin import BaseModelAdmin
from .models import Message, Messager


class MessageModelAdmin(BaseModelAdmin):
    list_display = ('receiver', 'sender', 'title', 'wrote_time', 'status') + BaseModelAdmin.list_display


class MessagerModelAdmin(BaseModelAdmin):
    list_display = ('message', 'status', 'backend_type') + BaseModelAdmin.list_display


admin.site.register(Message, MessageModelAdmin)
admin.site.register(Messager, MessagerModelAdmin)
