from django.conf import settings
from django.db import models
from apps.locations.help import LocationHelp, CityHelp, StateHelp, ZipcodeHelp
import uuid
from django.contrib.auth import get_permission_codename
# Create your models here.

class Location(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False,)
  location = models.CharField(max_length=200, unique=True, help_text=LocationHelp.location)
  street_address = models.CharField(max_length=200, unique=True, help_text=LocationHelp.street_address)
  city = models.ForeignKey('City', to_field='uuid', on_delete=models.PROTECT, related_name='locations_location_city', limit_choices_to={'deleted': False,}, help_text=LocationHelp.city)
  state = models.ForeignKey('State', to_field='uuid', on_delete=models.PROTECT, related_name='locations_location_state', limit_choices_to={'deleted': False,}, help_text=LocationHelp.state)
  zipcode = models.ForeignKey('Zipcode', to_field='uuid', on_delete=models.PROTECT, related_name='locations_location_zipcode', limit_choices_to={'deleted': False,}, help_text=LocationHelp.zipcode)
  google_place = models.URLField(max_length=2048, blank=True,null=True, help_text=LocationHelp.google_place)
  deleted = models.BooleanField(default=False) 
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='locations_location_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='locations_location_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'locations_location'
    get_latest_by = 'update_date'
    permissions = (('trash_location', 'Can soft delete location'),('restore_location', 'Can restore location'))
    verbose_name = 'Location'
    verbose_name_plural = 'Locations'

  def __str__(self):
    return self.location

class City(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False,)
  city = models.CharField(max_length=200, unique=True, help_text=CityHelp.city)
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='locations_city_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='locations_city_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'locations_city'
    get_latest_by = 'update_date'
    permissions = (('trash_city', 'Can soft delete city'),('restore_city', 'Can restore city'))
    verbose_name = 'City'
    verbose_name_plural = 'Cities'

  def __str__(self):
    return self.city

class State(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False,)
  state = models.CharField(max_length=200, unique=True, help_text=StateHelp.state)
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='locations_state_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='locations_state_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'locations_state'
    get_latest_by = 'update_date'
    permissions = (('trash_state', 'Can soft delete state'),('restore_state', 'Can restore state'))
    verbose_name = 'State'
    verbose_name_plural = 'States'

  def __str__(self):
    return self.state

class Zipcode(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False,)
  zipcode = models.CharField(max_length=200, unique=True, help_text=ZipcodeHelp.zipcode)
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='locations_zip_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='locations_zip_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'locations_zipcode'
    get_latest_by = 'update_date'
    permissions = (('trash_zipcode', 'Can soft delete zipcode'),('restore_zipcode', 'Can restore zipcode'))
    verbose_name = 'ZIP Code'
    verbose_name_plural = 'ZIP Codes'

  def __str__(self):
    return self.zipcode
