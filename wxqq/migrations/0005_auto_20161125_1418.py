# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-11-25 14:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wxqq', '0004_auto_20161103_2141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qq',
            name='bindsale',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sale.Sale'),
        ),
        migrations.AlterField(
            model_name='wx',
            name='bindsale',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sale.Sale'),
        ),
    ]
