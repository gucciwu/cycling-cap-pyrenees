from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext as _, gettext

from utils.data import guid
from utils.date import now
from .exceptions import PyrError


# exceptions
class UpdateWithoutTouchError(PyrError):
    def __init__(self, message):
        self.message = message


class UpdateDeletedError(PyrError):
    def __init__(self, message):
        self.message = message


def get_recycle_user():
    return get_user_model().objects.get_or_create(username='RECYCLE')[0]


def get_system_user():
    return get_user_model().objects.get_or_create(username='SYSTEM')[0]


def get_unknown_user():
    return get_user_model().objects.get_or_create(username='UNKNOWN')[0]


def get_collector_user():
    return get_user_model().objects.get_or_create(username='COLLECTOR')[0]


def get_user_from_request(request):
    user = request.user._wrapped if hasattr(request.user, '_wrapped') else request.user
    # skip anonymous user
    if user.is_authenticated:
        return user
    else:
        return None


class BaseQuerySet(QuerySet):

    def delete(self):
        self.update(deleted=True, force_update_deleted=True, modified_time=now())

    def force_delete(self):
        return super().delete()

    def restore(self):
        self.update(deleted=False, modified_time=now())

    def update(self, force_update_deleted=False, **kwargs):
        if not force_update_deleted and 'deleted' in kwargs.keys() and kwargs['deleted']:
            raise UpdateDeletedError(_("Deleted record can not be update!"))
        kwargs['modified_time'] = now()
        return super().update(**kwargs)


class BaseModelManager(models.Manager):
    use_for_related_fields = True

    def with_deleted(self):
        return BaseQuerySet(self.model, using=self._db)

    def deleted(self):
        return self.with_deleted().filter(deleted=True)

    def get_queryset(self):
        return self.with_deleted().exclude(deleted=True)


class BaseModel(models.Model):
    owner = models.ForeignKey(User, limit_choices_to={'is_active': True},
                              related_name="%(app_label)s_%(class)s_owner_related",
                              related_query_name="%(app_label)s_%(class)ss_owner",
                              on_delete=models.DO_NOTHING,
                              verbose_name=gettext("owner"), null=True)

    created_time = models.DateTimeField(auto_now_add=True,
                                        verbose_name=gettext("创建时间"))
    created_by = models.ForeignKey(User, limit_choices_to={'is_active': True},
                                   related_name="%(app_label)s_%(class)s_created_related",
                                   related_query_name="%(app_label)s_%(class)ss_created",
                                   on_delete=models.DO_NOTHING,
                                   verbose_name=gettext("创建人"), null=True)

    modified_time = models.DateTimeField(auto_now_add=True,
                                         verbose_name=gettext("最后修改时间"))
    modified_by = models.ForeignKey(User, limit_choices_to={'is_active': True},
                                    related_name="%(app_label)s_%(class)s_modified_related",
                                    related_query_name="%(app_label)s_%(class)ss_modified",
                                    on_delete=models.DO_NOTHING,
                                    verbose_name=gettext("最后修改人"), null=True)

    deleted = models.BooleanField(default=False, verbose_name=gettext("已删除"))
    pyr_guid = models.CharField(max_length=128, verbose_name=gettext("Pyrenees GUID"), unique=True, null=True)

    objects = BaseModelManager()

    # used in count
    countable = False

    def __str__(self):
        return '%s/%s' % (self.id, self.pyr_guid)

    """
    Update modified_by and modified_time without save
    """

    def _soft_touch(self, by_user=None):
        self.modified_time = now()
        if by_user is not None:
            self.modified_by = by_user

    """
    Update modified_by and modified_time fields, save immediately
    """

    def touch(self, by_user=None, force_update_deleted=False, update_all=False):
        if self.deleted and not force_update_deleted:
            return

        self._soft_touch(by_user)
        if update_all:
            self.save()
        else:
            self.save(update_fields=('modified_by', 'modified_time'))

    """
    For safety, the deleted instance should never update,
    but it can be force update by set @force_update_deleted with True
    """

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, force_update_deleted=False):

        if self.deleted and not force_update_deleted:
            raise UpdateDeletedError(_("Deleted record can not be update!"))

        self._soft_touch()
        self.modified_time = now()
        # set created_time and created_by in creating
        if self.pk is None:
            self.created_time = now()
            if not self.pyr_guid:
                self.pyr_guid = guid()
            if self.created_by is None:
                self.created_by = get_unknown_user()

        return super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        self.modified_time = now()
        self.deleted = True
        self.save(update_fields=('modified_by', 'modified_time', 'deleted'),
                  force_update_deleted=True)

    def force_delete(self, using=None):
        super().delete(using)

    def restore(self):
        # self._soft_touch()
        self.modified_time = now()
        self.deleted = False
        return self.save(update_fields=('modified_by', 'modified_time', 'deleted'))

    def set_user(self, user=None):
        if user is None:
            user = get_unknown_user()
        self.owner = user
        self.created_by = user
        self.modified_by = user

    class Meta:
        abstract = True
        get_latest_by = ['-modified_time']
        ordering = ['-modified_time']
