# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-15 19:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ops',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fixContent', models.CharField(max_length=300, verbose_name='\u7ef4\u62a4\u5185\u5bb9')),
                ('create', models.DateTimeField(verbose_name='\u521b\u5efa\u65f6\u95f4')),
            ],
        ),
    ]
