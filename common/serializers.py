from rest_framework import serializers
from django.contrib.auth.models import Group, Permission, User

from base.serializers import BaseHyperlinkedModelSerializer
from common.models import UserProfile


class UserSerializer(BaseHyperlinkedModelSerializer):

    class Meta:
        model = User
        exclude = ('password', 'groups', 'user_permissions')


class UserProfileSerializer(BaseHyperlinkedModelSerializer):
    auth_user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'


class SimpleUserProfileSerializer(BaseHyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class PermissionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Permission
        fields = ('url', 'name', 'content_type', 'codename')