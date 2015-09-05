# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ihunt', '0005_auto_20150830_1133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='teams',
            field=models.ManyToManyField(related_name='users', blank=True, to='ihunt.Team'),
        ),
        migrations.AlterUniqueTogether(
            name='team',
            unique_together=set([('name', 'at_event')]),
        ),
    ]
