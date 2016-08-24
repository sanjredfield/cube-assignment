# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-08-19 21:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videolearner', '0007_auto_20160820_0122'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userconfirmation',
            name='id',
        ),
        migrations.AlterField(
            model_name='userconfirmation',
            name='confirmation_code',
            field=models.TextField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='chain_address',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
