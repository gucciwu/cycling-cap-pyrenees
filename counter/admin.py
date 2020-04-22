from django.contrib import admin

from .models import Counter


class UserProfileModelAdmin(admin.ModelAdmin):
    list_display = ('guid', 'counter_type', 'value')
    readonly_fields = ('guid', 'counter_type', 'value')


admin.site.register(Counter, UserProfileModelAdmin)
