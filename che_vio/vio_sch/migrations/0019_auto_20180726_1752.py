# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-07-26 17:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vio_sch', '0018_auto_20180719_1506'),
    ]

    operations = [
        migrations.AddField(
            model_name='vioinfo',
            name='deal_status',
            field=models.IntegerField(blank=True, default=-1, null=True),
        ),
        migrations.AddField(
            model_name='vioinfo',
            name='pay_status',
            field=models.IntegerField(blank=True, default=-1, null=True),
        ),
    ]