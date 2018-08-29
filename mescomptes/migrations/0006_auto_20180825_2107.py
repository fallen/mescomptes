# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-08-25 19:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mescomptes', '0005_auto_20180825_1845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compte',
            name='opening_balance',
            field=models.FloatField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='credit',
            field=models.FloatField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='debit',
            field=models.FloatField(blank=True, default=0),
        ),
    ]
