# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20140914_1736'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClueSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateTimeField()),
                ('clues', models.ManyToManyField(to='app.Clue')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='team',
            name='current_clue',
            field=models.ForeignKey(default=1, to='app.Clue'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='team',
            name='current_clueset',
            field=models.ForeignKey(default=1, to='app.ClueSet'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='guess',
            name='by',
            field=models.ForeignKey(to='app.UserProfile'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='team',
            field=models.ForeignKey(related_name=b'users', to='app.Team'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(related_name=b'profile', to=settings.AUTH_USER_MODEL),
        ),
    ]
