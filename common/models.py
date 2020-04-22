from django.contrib.auth.models import AbstractUser, User
from django.db import models

from base.models import BaseModel
from entry.settings import DATABASE_TABLE_PREFIX


class UserProfile(BaseModel):
    auth_user = models.ForeignKey(User, limit_choices_to={'is_active': True}, related_name="auth_user",
                                  related_query_name="auth_user",
                                  on_delete=models.DO_NOTHING,
                                  verbose_name='user', null=False)
    email = models.EmailField(null=True, blank=True)
    signature = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    mobile = models.CharField(max_length=200, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    nickname = models.CharField(max_length=20)
    avatar = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.nickname

    class Meta:
        db_table = DATABASE_TABLE_PREFIX + 'user_profile'
        verbose_name = 'User Profile'
