# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-08-24 11:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videolearner', '0018_auto_20160824_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='chain_address',
            field=models.CharField(max_length=100),
        ),
    ]