# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-19 07:02
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0015_auto_20161019_0948'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='banned_to',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='banned_from',
            field=models.DateTimeField(default=datetime.datetime(2016, 10, 19, 7, 2, 1, 562000, tzinfo=utc), verbose_name='date banned'),
        ),
        migrations.AlterField(
            model_name='task',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2016, 10, 19, 7, 2, 1, 563000, tzinfo=utc), verbose_name='published date'),
        ),
    ]
