# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-08-25 21:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mescomptes', '0007_auto_20180825_2115'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categorie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='inscription',
            name='mensualiser',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='inscription',
            name='categorie',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mescomptes.Categorie'),
        ),
    ]
