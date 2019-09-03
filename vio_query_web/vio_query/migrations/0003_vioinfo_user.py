# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-06-10 16:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vio_query', '0002_remove_vioinfo_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='vioinfo',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vio_query.UserInfo'),
        ),
    ]