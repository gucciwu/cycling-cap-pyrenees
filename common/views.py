import logging

from django.contrib.auth import get_user_model, logout
from django.contrib.auth.models import Group, Permission, User
from django.db.models import Q
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny

from base.http import AlpsRestResponse
from base.models import get_user_from_request
from base.views import BaseViewSet
from counter.models import Counter
from counter.services import count
from entry.settings import MEDIA_ROOT, MEDIA_PATH_AVATAR, SITE
from message.models import Message, MESSAGE_STATUS_SUCCESS
from message.services import send_active_mail
from utils.action_history import log_action, log_change, Actions
from utils.data import guid
from utils.filesystem import LocalFile
from .authentications import get_user_roles
from .models import UserProfile
from .serializers import UserSerializer, GroupSerializer, PermissionSerializer, UserProfileSerializer
from .services import create_user_profile, get_user_profile

logger = logging.getLogger(__name__)

ERROR_MISSING_EMAIL = {"error_code": 101, "error_message": "missing email"}
ERROR_PASSWORD_MISMATCH = {"error_code": 102, "error_message": "password and password_check mismatch"}
ERROR_EMAIL_EXIST = {"error_code": 103, "error_message": "email exist"}
ERROR_ALREADY_ACTIVATED = {"error_code": 104, "error_message": "user has already activated"}
ERROR_EMAIL_CODE_MISMATCH = {"error_code": 105, "error_message": "email and code mismatch"}
ERROR_NOT_REGISTER = {"error_code": 106, "error_message": "not register"}


class UserProfileViewSet(BaseViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all().order_by('-created_time')

    def get_queryset(self):
        queryset = UserProfile.objects.all().order_by('-created_time')
        keyword = self.request.query_params.get('keyword', None)
        if keyword is not None:
            queryset = queryset.filter(Q(nickname__istartswith=keyword) | Q(email__istartswith=keyword) | Q(mobile__istartswith=keyword))
        return queryset

    @action(detail=False, methods=['GET'], permission_classes=(IsAuthenticated,))
    @never_cache
    def current(self, request):
        user = get_user_from_request(request)
        if user.is_active:
            profile = get_user_profile(user)
            if profile is None:
                return AlpsRestResponse.success({"roles": 'guest'})
            serializer = self.get_serializer(profile, many=False)
            return AlpsRestResponse.success({"user": serializer.data, "roles": get_user_roles(user)})
        else:
            return AlpsRestResponse.fail(status=status.HTTP_403_FORBIDDEN, error_message='inactive user')

    @action(detail=False, methods=['POST'], permission_classes=(AllowAny,))
    def register(self, request):
        try:
            email = request.data["email"]
            password = request.data["password"]
            password_check = request.data["confirm"]
        except KeyError as err:
            logger.error(err)
            return AlpsRestResponse.fail(status=status.HTTP_400_BAD_REQUEST)

        if email is None or email == "":
            return AlpsRestResponse.success(**ERROR_MISSING_EMAIL)

        if password is None or password != password_check:
            return AlpsRestResponse.success(**ERROR_PASSWORD_MISMATCH)

        try:
            get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist as err:
            pass
        else:
            return AlpsRestResponse.success(**ERROR_EMAIL_EXIST)

        username = email.split('@')[0]
        try:
            get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist as err:
            pass
        else:
            username = guid()  # user name already exist, instead of GUID

        user = get_user_model()(username=username, email=email)
        user.set_password(password)
        user.is_active = False  # default is True
        user.save()
        log_action(user, user, Actions.REGISTERING, "Registered successfully")
        logger.info("Registered successfully with %s" % username)
        serializer = UserSerializer(user, context={'request': request})

        # send active email
        send_active_mail(user)
        return AlpsRestResponse.success(serializer.data)

    @action(detail=False, methods=['POST'], permission_classes=(AllowAny,), url_path="active/email")
    def send_active_email(self, request):
        try:
            email = request.data["email"]
        except KeyError as err:
            logger.error(err)
            return AlpsRestResponse.fail(status=status.HTTP_400_BAD_REQUEST)

        if email is None or email == "":
            return AlpsRestResponse.success(**ERROR_MISSING_EMAIL)

        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist as err:
            return AlpsRestResponse.success(**ERROR_NOT_REGISTER)

        if user.is_active:
            return AlpsRestResponse.success(**ERROR_ALREADY_ACTIVATED)

        send_active_mail(user)
        return AlpsRestResponse.success()

    @action(detail=False, methods=['POST'], permission_classes=(AllowAny,))
    def active(self, request):
        email = request.data.get('email', None)
        code = request.data.get('code', None)
        if email is None or code is None:
            return AlpsRestResponse.fail(status=status.HTTP_400_BAD_REQUEST)
        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist as err:
            return AlpsRestResponse.fail(status=status.HTTP_404_NOT_FOUND)

        if user.is_active:
            return AlpsRestResponse.success(**ERROR_ALREADY_ACTIVATED)

        messages = Message.objects.filter(content__contains=code) \
            .filter(receiver=user) \
            .filter(status=MESSAGE_STATUS_SUCCESS)
        if len(messages) > 0:
            user.is_active = True
            user.save()
            # create user profile
            create_user_profile(user)
            log_action(user, user, Actions.USER_ACTIVATION, "User %s has been activated" % user.username)
            logger.info("User %s has been activated" % user.username)
            return AlpsRestResponse.success(status=status.HTTP_202_ACCEPTED)
        else:
            logger.debug("Can't find active email for user %s" % user.username)
            return AlpsRestResponse.fail(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    def avatar(self, request, pk=None):
        file = request.FILES['file']
        if file is None:
            return AlpsRestResponse.fail(error_code=-2, error_message="File data not found",
                                         status=status.HTTP_400_BAD_REQUEST)

        user = get_user_from_request(request)
        if user is None:
            return AlpsRestResponse.fail(status=status.HTTP_404_NOT_FOUND)

        if not LocalFile.is_image(file.content_type):
            logger.debug("User %s change avatar failed, file %s is not supported" % (user.username, file.name))
            return AlpsRestResponse.fail(error_code=-2, error_message="Unsupperted file type",
                                         status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        profile = self.get_object()
        if profile.auth_user != user:
            return AlpsRestResponse.fail(error_code=-2, error_message="can't change other user's avatar",
                                         status=status.HTTP_403_FORBIDDEN)
        # delete old one if exist
        if profile.avatar:
            LocalFile.delete(MEDIA_ROOT + profile.avatar)

        destination = LocalFile.save(request, to_path=MEDIA_PATH_AVATAR)
        profile.avatar = destination
        profile.save()
        if destination is None:
            return AlpsRestResponse.fail(error_code=-2, error_message="Failed save file data",
                                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        log_change(user, user, "%s has changed avatar with file %s " % (user.username, profile.avatar))
        logger.info("%s has changed avatar with file %s " % (user.username, profile.avatar))
        return AlpsRestResponse.success(UserProfileSerializer(profile, context={"request": request}).data)

    @action(detail=False, methods=['GET', 'POST'], permission_classes=(IsAuthenticated,))
    def logout(self, request):
        logout(request)
        return AlpsRestResponse.success('logout successfully')


class GroupViewSet(BaseViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PermissionViewSet(BaseViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


class UserViewSet(BaseViewSet):
    """
    API endpoint that allows auth user to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        add profile information
        """
        pk = kwargs.get(self.lookup_field, None)

        if pk is None:
            return AlpsRestResponse.fail(status=status.HTTP_404_NOT_FOUND)
        user = self.get_object()
        if user is None:
            return AlpsRestResponse.fail(status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, context={'request': request})
        data = serializer.data
        try:
            profile = UserProfile.objects.get(auth_user=user)
            views = count(profile, Counter.TYPE_VIEW)
            profile_data = UserProfileSerializer(profile, context={'request': request}).data
        except UserProfile.DoesNotExist as err:
            profile_data = None
            views = 0
        data.update({'profile': profile_data})
        return AlpsRestResponse.success(data, extra={'views': views})

    @action(detail=True, methods=['GET'])
    def profile(self, request, pk=None):
        user = self.get_object()
        profile = get_user_profile(user)
        if profile is not None:
            return AlpsRestResponse.success(UserProfileSerializer(profile, context={"request": request}).data)
        else:
            return AlpsRestResponse.fail(status=status.HTTP_404_NOT_FOUND)


def home_page(request):
    return redirect(SITE['root'])
