# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-18 13:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0004_auto_20161018_1548'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalLimits',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_launch', models.IntegerField(default=5)),
                ('task_max_time', models.IntegerField(default=240)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='banned',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='launch_score',
            field=models.IntegerField(default=0),
        ),
    ]
