# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-06-23 09:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vio_sch', '0022_vehicleinfosz_vioinfosz'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vioinfo',
            name='vio_activity',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]