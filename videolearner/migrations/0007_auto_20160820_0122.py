# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-08-19 19:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videolearner', '0006_auto_20160819_1857'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserVideoSubscription',
            new_name='UserVideo',
        ),
        migrations.AddField(
            model_name='subscription',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
