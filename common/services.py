import logging

from base.services import random_nickname
from common.models import UserProfile
from utils.action_history import log_addition

logger = logging.getLogger(__name__)


def create_user_profile(user):
    if user is None:
        return None
    profile = UserProfile()
    profile.email = user.email
    profile.nickname = random_nickname()
    profile.auth_user = user
    profile.save()
    log_addition(user, profile, "User profile created successfully!")
    return profile


def get_user_profile(user):
    profile = None
    try:
        profile = UserProfile.objects.get(auth_user=user)
    except UserProfile.DoesNotExist as err:
        logger.error('Failed get user profile! %s' % str(user))
    except UserProfile.MultipleObjectsReturned as err:
        logger.error('Multiple user profile found! %s' % str(user))
    finally:
        return profile
