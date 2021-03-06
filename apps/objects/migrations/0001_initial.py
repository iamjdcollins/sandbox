# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-09 16:30
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import mptt.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_auto_20170905_0841'),
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('node_title', models.CharField(max_length=200)),
                ('url', models.CharField(db_index=True, max_length=2000, unique=True)),
                ('node_type', models.CharField(blank=True, db_index=True, editable=False, max_length=200, null=True)),
                ('content_type', models.CharField(blank=True, db_index=True, editable=False, max_length=200, null=True)),
                ('menu_item', models.BooleanField(db_index=True, default=False)),
                ('menu_title', models.CharField(blank=True, max_length=200, null=True)),
                ('create_date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('update_date', models.DateTimeField(auto_now=True, db_index=True)),
                ('published', models.BooleanField(db_index=True, default=True)),
                ('deleted', models.BooleanField(db_index=True, default=False)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
            ],
            options={
                'db_table': 'objects_node',
                'get_latest_by': 'create_date',
                'verbose_name': 'Node',
                'verbose_name_plural': 'Nodes',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('user_type', models.CharField(blank=True, editable=False, max_length=200, null=True)),
                ('user_node', models.OneToOneField(db_column='user_node', on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='objects.Node')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'objects_user',
                'get_latest_by': 'create_date',
                'verbose_name': 'User',
                'default_manager_name': 'objects',
                'verbose_name_plural': 'Users',
            },
            bases=('objects.node', models.Model),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('image_type', models.CharField(blank=True, editable=False, max_length=200, null=True)),
                ('image_node', models.OneToOneField(db_column='image_node', on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='objects.Node')),
            ],
            options={
                'db_table': 'objects_image',
                'get_latest_by': 'create_date',
                'verbose_name': 'Image',
                'verbose_name_plural': 'Images',
            },
            bases=('objects.node',),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('page_type', models.CharField(blank=True, editable=False, max_length=200, null=True)),
                ('page_node', models.OneToOneField(db_column='page_node', on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='objects.Node')),
            ],
            options={
                'db_table': 'objects_page',
                'get_latest_by': 'create_date',
                'verbose_name': 'Page',
                'verbose_name_plural': 'Pages',
            },
            bases=('objects.node',),
        ),
        migrations.CreateModel(
            name='Taxonomy',
            fields=[
                ('taxonomy_type', models.CharField(blank=True, editable=False, max_length=200, null=True)),
                ('taxonomy_node', models.OneToOneField(db_column='taxonomy_node', on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='objects.Node')),
            ],
            options={
                'db_table': 'objects_taxonomy',
                'get_latest_by': 'create_date',
                'verbose_name': 'Taxonomy',
                'verbose_name_plural': 'Taxonomies',
            },
            bases=('objects.node',),
        ),
        migrations.AddField(
            model_name='node',
            name='create_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='objects_node_create_user', to=settings.AUTH_USER_MODEL, to_field='uuid'),
        ),
        migrations.AddField(
            model_name='node',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='objects_node_parent', to='objects.Node'),
        ),
        migrations.AddField(
            model_name='node',
            name='update_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='objects_node_update_user', to=settings.AUTH_USER_MODEL, to_field='uuid'),
        ),
        migrations.AlterUniqueTogether(
            name='node',
            unique_together=set([('parent', 'node_title')]),
        ),
    ]
