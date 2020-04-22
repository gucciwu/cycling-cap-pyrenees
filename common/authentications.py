from .serializers import UserSerializer
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def get_user_roles(user):
    if not user:
        return []

    roles = []

    if user.is_staff:
        roles.append('user')
    if user.is_superuser:
        roles.append('admin')

    return roles


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data,
        'roles': get_user_roles(user)
    }


class EnhancedAuthentication(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username, password, **kwargs)
        if user is None:
            try:
                validate_email(username)
                user_model = get_user_model()
                user = user_model.objects.get(email=username)
                if user is not None and user.check_password(password) and self.user_can_authenticate(user):
                    return user
            except ValidationError:
                return None
            else:
                return None
        return None
            




