# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-08-22 23:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videolearner', '0015_auto_20160823_0453'),
    ]

    operations = [
        migrations.AddField(
            model_name='uservideo',
            name='credits_awarded',
            field=models.IntegerField(default=0),
        ),
    ]
