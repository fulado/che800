# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-06-25 23:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vio_sch', '0003_auto_20180624_1714'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicleinfo',
            name='vehicle_type',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]