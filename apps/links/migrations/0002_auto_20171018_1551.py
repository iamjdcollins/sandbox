# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-18 21:51
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('links', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='resourcelink',
            old_name='node',
            new_name='related_nodes',
        ),
    ]
