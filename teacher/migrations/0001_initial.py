# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-10-17 19:12
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bursar', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpotTeacher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teacherId', models.CharField(max_length=20, unique=True, verbose_name='\u8001\u5e08ID')),
                ('company', models.CharField(max_length=30, verbose_name='\u516c\u53f8')),
                ('department', models.CharField(max_length=30, verbose_name='\u90e8\u95e8')),
                ('group', models.CharField(blank=True, max_length=30, null=True, verbose_name='\u7ec4')),
                ('binduser', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teacherId', models.CharField(max_length=20, unique=True, verbose_name='\u8001\u5e08ID')),
                ('company', models.CharField(max_length=30, verbose_name='\u516c\u53f8')),
                ('department', models.CharField(max_length=30, verbose_name='\u90e8\u95e8')),
                ('group', models.CharField(blank=True, max_length=30, null=True, verbose_name='\u7ec4')),
                ('bindbursar', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bursar.Bursar')),
                ('bindspotteacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='teacher.SpotTeacher')),
                ('binduser', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
