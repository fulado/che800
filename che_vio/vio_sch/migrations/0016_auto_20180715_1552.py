# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-07-15 15:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vio_sch', '0015_loginfo_city'),
    ]

    operations = [
        migrations.RenameField(
            model_name='loginfo',
            old_name='comments',
            new_name='msg',
        ),
        migrations.AddField(
            model_name='loginfo',
            name='origin_msg',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='loginfo',
            name='origin_status',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
