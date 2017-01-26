# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-20 08:07
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0020_auto_20161020_1107'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='node_id',
            field=models.OneToOneField(default=-1, on_delete=django.db.models.deletion.CASCADE, to='interface.Node'),
        ),
        migrations.AlterField(
            model_name='banned',
            name='banned_from',
            field=models.DateTimeField(default=datetime.datetime(2016, 10, 20, 8, 7, 53, 576000, tzinfo=utc), verbose_name='date banned'),
        ),
        migrations.AlterField(
            model_name='banned',
            name='banned_to',
            field=models.DateTimeField(default=datetime.datetime(2016, 10, 22, 8, 7, 53, 576000, tzinfo=utc), verbose_name='date unbanned'),
        ),
        migrations.AlterField(
            model_name='task',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2016, 10, 20, 8, 7, 53, 577000, tzinfo=utc), verbose_name='published date'),
        ),
    ]