from django.utils.translation import gettext

from base.models import BaseModel
from django.db import models

from entry.settings import DATABASE_TABLE_PREFIX


class Dictionary(BaseModel):
    dict_entry = models.CharField(max_length=200, null=False)
    dict_key = models.CharField(max_length=200, null=False)
    dict_value = models.TextField(null=False)
    dict_remark = models.TextField(max_length=500, null=True, blank=True, default="")

    def __str__(self):
        return self.dict_entry + '/' + self.dict_key

    class Meta:
        db_table = DATABASE_TABLE_PREFIX + 'dictionary'
        verbose_name_plural = gettext('dictionaries')





