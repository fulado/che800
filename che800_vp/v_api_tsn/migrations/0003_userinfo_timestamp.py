# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-03-11 20:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('v_api_tsn', '0002_viocode'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='timestamp',
            field=models.IntegerField(default=0),
        ),
    ]
