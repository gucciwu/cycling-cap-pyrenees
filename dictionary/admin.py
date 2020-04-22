from django.contrib import admin
from .models import Dictionary
from base.admin import BaseModelAdmin


class DictionaryModelAdmin(BaseModelAdmin):
    list_display = ('dict_entry', 'dict_key') + BaseModelAdmin.list_display
    list_display_links = ('dict_entry', 'dict_key')


admin.site.register(Dictionary, DictionaryModelAdmin)
