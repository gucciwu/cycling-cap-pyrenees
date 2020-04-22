from django.db import models

from entry.settings import DATABASE_TABLE_PREFIX


class Counter(models.Model):
    TYPE_VIEW = 1
    TYPES = [(TYPE_VIEW, 'view')]

    value = models.BigIntegerField(default=0)
    guid = models.CharField(max_length=128)
    counter_type = models.IntegerField(choices=TYPES, default=TYPE_VIEW)

    def __str__(self):
        return '%s-%s' % (self.value, self.guid)

    def add(self):
        self.value = self.value + 1
        self.save()

    class Meta:
        db_table = DATABASE_TABLE_PREFIX + 'counter'
