# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-10-17 19:26
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0003_auto_20161017_1923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='create',
            field=models.DateTimeField(default=datetime.datetime(2016, 10, 17, 19, 26, 22, 61000), verbose_name='\u4ea4\u6613\u65f6\u95f4'),
        ),
    ]
