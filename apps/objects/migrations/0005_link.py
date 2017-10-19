# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-18 21:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('objects', '0004_auto_20171013_1432'),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('link_type', models.CharField(blank=True, editable=False, max_length=200, null=True)),
                ('link_node', models.OneToOneField(db_column='link_node', editable=False, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='objects.Node')),
            ],
            options={
                'verbose_name': 'Link',
                'get_latest_by': 'create_date',
                'verbose_name_plural': 'Links',
                'db_table': 'objects_link',
            },
            bases=('objects.node',),
        ),
    ]