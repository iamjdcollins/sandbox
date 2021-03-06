# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-12 18:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('objects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DirectoryEntry',
            fields=[
                ('directoryentry_type', models.CharField(blank=True, editable=False, max_length=200, null=True)),
                ('directoryentry_node', models.OneToOneField(db_column='directoryentry_node', on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='objects.Node')),
            ],
            options={
                'db_table': 'objects_directoryentry',
                'verbose_name_plural': 'Directory Entries',
                'verbose_name': 'Directory Entry',
                'get_latest_by': 'create_date',
            },
            bases=('objects.node',),
        ),
    ]
