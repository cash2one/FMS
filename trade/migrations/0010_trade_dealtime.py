# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-11-29 14:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0009_auto_20161125_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='trade',
            name='dealtime',
            field=models.DateTimeField(default=None, null=True, verbose_name='\u63d0\u4ea4\u4ea4\u6613\u65f6\u95f4'),
        ),
    ]
