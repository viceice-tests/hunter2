# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20140914_1422'),
    ]

    operations = [
        migrations.CreateModel(
            name='Guess',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guess', models.TextField()),
                ('for_clue', models.ForeignKey(to='app.Clue')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
