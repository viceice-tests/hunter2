# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from sortedm2m.operations import AlterSortedManyToManyField
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ihunt', '0002_event_current'),
    ]

    operations = [
        AlterSortedManyToManyField(
            model_name='clueset',
            name='clues',
            field=sortedm2m.fields.SortedManyToManyField(to='ihunt.Clue', help_text=None),
        ),
    ]
