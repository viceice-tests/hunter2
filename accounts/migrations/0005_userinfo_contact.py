# Generated by Django 2.1.7 on 2019-03-30 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20190223_1016'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='contact',
            field=models.BooleanField(help_text='May we contact you about this or future events?', null=True, verbose_name=''),
        ),
    ]
