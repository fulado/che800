# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-06-26 13:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vio_sch', '0005_auto_20180626_1344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicleinfo',
            name='city',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
