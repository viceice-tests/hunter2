# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ihunt', '0006_auto_20150905_1948'),
    ]

    operations = [
        migrations.CreateModel(
            name='PuzzleSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('start_date', models.DateTimeField()),
                ('event', models.ForeignKey(to='ihunt.Event', related_name='puzzlesets')),
            ],
        ),
        migrations.RenameModel(
            old_name='Clue',
            new_name='Puzzle',
        ),
        migrations.RemoveField(
            model_name='clueset',
            name='clues',
        ),
        migrations.RemoveField(
            model_name='clueset',
            name='event',
        ),
        migrations.AlterModelOptions(
            name='guess',
            options={'verbose_name_plural': 'Guesses'},
        ),
        migrations.RenameField(
            model_name='guess',
            old_name='for_clue',
            new_name='for_puzzle',
        ),
        migrations.RemoveField(
            model_name='answer',
            name='for_clue',
        ),
        migrations.AddField(
            model_name='answer',
            name='for_puzzle',
            field=models.ForeignKey(to='ihunt.Puzzle', default=None, related_name='answers'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='ClueSet',
        ),
        migrations.AddField(
            model_name='puzzleset',
            name='puzzles',
            field=sortedm2m.fields.SortedManyToManyField(to='ihunt.Puzzle', help_text=None),
        ),
    ]
