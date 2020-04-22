from django.contrib.admin.models import LogEntry, DELETION, CHANGE, ADDITION


class Actions:
    UNKNOWN = -1
    DELETION = DELETION
    CHANGE = CHANGE
    ADDITION = ADDITION
    CREATION = ADDITION
    SOFT_DELETION = 4
    UPLOAD = 5
    REGISTERING = 6
    USER_ACTIVATION = 7


def get_content_type_for_model(obj):
    # Since this module gets imported in the application's root package,
    # it cannot import models from other applications at the module level.
    from django.contrib.contenttypes.models import ContentType
    return ContentType.objects.get_for_model(obj, for_concrete_model=False)


def log_action(user, obj, action, message=''):
    return LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=get_content_type_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=repr(obj),
        action_flag=action,
        change_message=message,
    )


def log_soft_deletion(user, obj, message=''):
    """
    Log that an object has been successfully soft deleted.

    The default implementation creates an admin LogEntry object.
    """
    return log_action(user, obj, Actions.SOFT_DELETION, message)


def log_deletion(user, obj, message=''):
    """
    Log that an object has been successfully soft deleted.

    The default implementation creates an admin LogEntry object.
    """
    return log_action(user, obj, Actions.DELETION, message)


def log_change(user, obj, message=''):
    """
    Log that an object has been successfully changed.

    The default implementation creates an admin LogEntry object.
    """
    return log_action(user, obj, Actions.CHANGE, message)


def log_addition(user, obj, message=''):
    """
    Log that an object has been successfully added.

    The default implementation creates an admin LogEntry object.
    """
    return log_action(user, obj, Actions.ADDITION, message)
