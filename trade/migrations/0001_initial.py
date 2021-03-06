# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-10-17 19:12
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(default=0, verbose_name='\u4ea4\u6613\u72b6\u6001')),
                ('stockid', models.CharField(max_length=30, verbose_name='\u4ea7\u54c1ID')),
                ('stockname', models.CharField(max_length=30, verbose_name='\u4ea7\u54c1\u540d\u79f0')),
                ('buyprice', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='\u8d2d\u5165\u4ef7\u683c')),
                ('buycount', models.IntegerField(default=0, verbose_name='\u8d2d\u5165\u6570\u91cf')),
                ('buycash', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='\u8d2d\u5165\u603b\u4ef7')),
                ('share', models.CharField(default='5|5', max_length=5, verbose_name='\u5206\u6210\u6bd4\u4f8b')),
                ('sellprice', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='\u5356\u51fa\u4ef7\u683c')),
                ('income', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='\u76c8\u5229')),
                ('commission', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='\u624b\u7eed\u8d39')),
                ('paytype', models.CharField(default='', max_length=30, verbose_name='\u6536\u6b3e\u7c7b\u578b')),
                ('create', models.DateTimeField(default=datetime.datetime(2016, 10, 17, 19, 12, 18, 718000), verbose_name='\u4ea4\u6613\u65f6\u95f4')),
                ('paytime', models.DateTimeField(default=None, null=True, verbose_name='\u6536\u6b3e\u65f6\u95f4')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.Customer')),
            ],
        ),
    ]
