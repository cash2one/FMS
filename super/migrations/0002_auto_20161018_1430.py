# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-10-18 14:30
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('super', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transmission',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
