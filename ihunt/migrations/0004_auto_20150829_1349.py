# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ihunt', '0003_auto_20150829_0930'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='current_clue',
        ),
        migrations.RemoveField(
            model_name='team',
            name='current_clueset',
        ),
    ]
