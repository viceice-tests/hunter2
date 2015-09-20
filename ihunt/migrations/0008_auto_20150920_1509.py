# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ihunt', '0007_auto_20150920_1425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='puzzleset',
            name='puzzles',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text=None, to='ihunt.Puzzle'),
        ),
    ]
