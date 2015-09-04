# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ihunt', '0004_auto_20150829_1349'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='team',
        ),
        migrations.AddField(
            model_name='team',
            name='at_event',
            field=models.ForeignKey(related_name='event', default=None, to='ihunt.Event'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='teams',
            field=models.ManyToManyField(to='ihunt.Team'),
        ),
    ]
