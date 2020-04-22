from django.contrib import admin
from django.contrib.auth.models import Permission

from base.admin import BaseModelAdmin
from .models import UserProfile


class UserProfileModelAdmin(BaseModelAdmin):
    list_display = ('nickname', 'email', 'mobile') + BaseModelAdmin.list_display


class GroupModelAdmin(admin.ModelAdmin):
    list_display = ('name', )


class PermissionModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'content_type', 'codename')


# class UserObjectPermissionModelAdmin(admin.ModelAdmin):
#     list_display = ('user', 'permission', 'object_pk')
#
#
# class GroupObjectPermissionModelAdmin(admin.ModelAdmin):
#     list_display = ('group', 'permission', 'object_pk')


admin.site.register(UserProfile, UserProfileModelAdmin)
admin.site.register(Permission, PermissionModelAdmin)
# admin.site.register(UserObjectPermission, UserObjectPermissionModelAdmin)
# admin.site.register(GroupObjectPermission, GroupObjectPermissionModelAdmin)
