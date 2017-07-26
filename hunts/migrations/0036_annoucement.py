# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-25 21:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import enumfields.fields
import hunts.models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20170715_1417'),
        ('hunts', '0035_auto_20170722_1111'),
    ]

    operations = [
        migrations.CreateModel(
            name='Annoucement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('posted', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField(blank=True)),
                ('type', enumfields.fields.EnumField(enum=hunts.models.AnnoucmentType, max_length=1)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='announcements', to='events.Event')),
                ('puzzle', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='announcements', to='hunts.Puzzle')),
            ],
        ),
    ]
