# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-08-19 12:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('videolearner', '0002_auto_20160819_1807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='uservideosubscription',
            name='subscribed_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='video',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
