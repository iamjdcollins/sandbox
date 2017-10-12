# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-09 16:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('objects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('title', models.CharField(db_column='city', db_index=True, max_length=200, unique=True)),
                ('city_taxonomy_node', models.OneToOneField(db_column='city_taxonomy_node', on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='objects.Taxonomy')),
            ],
            options={
                'db_table': 'taxonomy_city',
                'get_latest_by': 'update_date',
                'verbose_name': 'City',
                'permissions': (('trash_city', 'Can soft delete city'), ('restore_city', 'Can restore city')),
                'verbose_name_plural': 'Cities',
            },
            bases=('objects.taxonomy',),
            managers=[
                ('_tree_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('title', models.CharField(db_column='language', db_index=True, max_length=200, unique=True, verbose_name='Language')),
                ('native_language', models.CharField(max_length=200, unique=True, verbose_name='Native Language Spelling')),
                ('language_code', models.CharField(max_length=5, unique=True, verbose_name='Language Code')),
                ('language_taxonomy_node', models.OneToOneField(db_column='language_taxonomy_node', on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='objects.Taxonomy')),
            ],
            options={
                'db_table': 'taxonomy_language',
                'get_latest_by': 'update_date',
                'verbose_name': 'Language',
                'permissions': (('trash_language', 'Can soft delete language'), ('restore_language', 'Can restore language')),
                'verbose_name_plural': 'Languages',
            },
            bases=('objects.taxonomy',),
            managers=[
                ('_tree_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('title', models.CharField(db_column='location', db_index=True, max_length=200, unique=True)),
                ('street_address', models.CharField(max_length=200, unique=True)),
                ('google_place', models.URLField(blank=True, max_length=2048, null=True)),
                ('location_taxonomy_node', models.OneToOneField(db_column='location_taxonomy_node', on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='objects.Taxonomy')),
                ('location_city', models.ForeignKey(db_column='city', on_delete=django.db.models.deletion.PROTECT, related_name='taxonomy_location_city', to='taxonomy.City')),
            ],
            options={
                'db_table': 'taxonomy_location',
                'get_latest_by': 'update_date',
                'verbose_name': 'Location',
                'permissions': (('trash_location', 'Can soft delete location'), ('restore_location', 'Can restore location')),
                'verbose_name_plural': 'Locations',
            },
            bases=('objects.taxonomy',),
            managers=[
                ('_tree_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='OpenEnrollmentStatus',
            fields=[
                ('title', models.CharField(db_index=True, max_length=200, unique=True)),
                ('openenrollmentstatus_taxonomy_node', models.OneToOneField(db_column='openenrollmentstatus_taxonomy_node', on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='objects.Taxonomy')),
            ],
            options={
                'db_table': 'taxonomy_openenrollmentstatus',
                'get_latest_by': 'update_date',
                'verbose_name': 'Open Enrollment Status',
                'permissions': (('trash_openenrollmentstatus', 'Can soft delete school open enrollment status'), ('restore_openenrollmentstatus', 'Can restore school open enrollment status')),
                'verbose_name_plural': 'Open Enrollment Statuses',
            },
            bases=('objects.taxonomy',),
            managers=[
                ('_tree_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='SchoolType',
            fields=[
                ('title', models.CharField(db_index=True, max_length=200, unique=True)),
                ('schooltype_taxonomy_node', models.OneToOneField(db_column='schooltype_taxonomy_node', on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='objects.Taxonomy')),
            ],
            options={
                'db_table': 'taxonomy_schooltype',
                'get_latest_by': 'update_date',
                'verbose_name': 'School Type',
                'permissions': (('trash_schooltype', 'Can soft delete school type'), ('restore_schooltype', 'Can restore school type')),
                'verbose_name_plural': 'School Types',
            },
            bases=('objects.taxonomy',),
            managers=[
                ('_tree_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('title', models.CharField(db_column='state', db_index=True, max_length=200, unique=True)),
                ('state_taxonomy_node', models.OneToOneField(db_column='state_taxonomy_node', on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='objects.Taxonomy')),
            ],
            options={
                'db_table': 'taxonomy_state',
                'get_latest_by': 'update_date',
                'verbose_name': 'State',
                'permissions': (('trash_state', 'Can soft delete state'), ('restore_state', 'Can restore state')),
                'verbose_name_plural': 'States',
            },
            bases=('objects.taxonomy',),
            managers=[
                ('_tree_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='TranslationType',
            fields=[
                ('title', models.CharField(db_column='translationtype', db_index=True, max_length=200, unique=True, verbose_name='Translation Link Type')),
                ('translationtype_taxonomy_node', models.OneToOneField(db_column='translationtype_taxonomy_node', on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='objects.Taxonomy')),
            ],
            options={
                'db_table': 'taxonomy_translationtype',
                'get_latest_by': 'update_date',
                'verbose_name': 'Translation Type',
                'permissions': (('trash_translationtype', 'Can soft delete translation type'), ('restore_translationtype', 'Can restore translation type')),
                'verbose_name_plural': 'Translation Types',
            },
            bases=('objects.taxonomy',),
            managers=[
                ('_tree_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Zipcode',
            fields=[
                ('title', models.CharField(db_column='zipcode', db_index=True, max_length=200, unique=True)),
                ('zipcode_taxonomy_node', models.OneToOneField(db_column='zipcode_taxonomy_node', on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='objects.Taxonomy')),
            ],
            options={
                'db_table': 'taxonomy_zipcode',
                'get_latest_by': 'update_date',
                'verbose_name': 'ZIP Code',
                'permissions': (('trash_zipcode', 'Can soft delete zipcode'), ('restore_zipcode', 'Can restore zipcode')),
                'verbose_name_plural': 'ZIP Codes',
            },
            bases=('objects.taxonomy',),
            managers=[
                ('_tree_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='location',
            name='location_state',
            field=models.ForeignKey(db_column='state', on_delete=django.db.models.deletion.PROTECT, related_name='taxonomy_location_state', to='taxonomy.State'),
        ),
        migrations.AddField(
            model_name='location',
            name='location_zipcode',
            field=models.ForeignKey(db_column='zipcode', on_delete=django.db.models.deletion.PROTECT, related_name='taxonomy_location_zipcode', to='taxonomy.Zipcode'),
        ),
        migrations.AddField(
            model_name='language',
            name='language_translationtype',
            field=models.ForeignKey(db_column='translationtype', on_delete=django.db.models.deletion.PROTECT, related_name='taxonomy_language_translationtype', to='taxonomy.TranslationType', verbose_name='Translation Type'),
        ),
    ]
