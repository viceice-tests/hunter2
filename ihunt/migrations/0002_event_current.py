# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ihunt', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='current',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
