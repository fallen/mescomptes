# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-08-24 13:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mescomptes', '0003_compte_devise'),
    ]

    operations = [
        migrations.AddField(
            model_name='devise',
            name='symbol',
            field=models.TextField(default='€'),
            preserve_default=False,
        ),
    ]
