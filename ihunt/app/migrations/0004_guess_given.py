# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_guess'),
    ]

    operations = [
        migrations.AddField(
            model_name='guess',
            name='given',
            field=models.DateTimeField(default=datetime.date(2014, 9, 14), auto_now_add=True),
            preserve_default=False,
        ),
    ]
