from django.conf import settings
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from guardian.shortcuts import assign_perm
from ckeditor.fields import RichTextField
from treebeard.mp_tree import MP_Node
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import Group
import apps.common.functions
#from apps.pages.models import Page
from apps.sitestructure.help import SiteStructureHelp
import uuid
from django.contrib.auth import get_permission_codename

# Create your models here.

class SiteStructure(MPTTModel):
  id = models.AutoField(primary_key=True)
  site_title = models.CharField(max_length=200,)
  menu_title = models.CharField(max_length=200, null=True, blank=True)
  menu_item = models.BooleanField(default=False)
  url = models.CharField(max_length=2000, unique=True, db_index=True)
  parent = TreeForeignKey('self', null=True, blank=True, related_name='sitestructure_sitestructure_parent', db_index=True)
  content_type = models.CharField(max_length=200, editable=False, null=True, blank=True)
  primary_contact = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.PROTECT, related_name='sitestructure_sitestructure_primary_contact',null=True, blank=False)
  #create_date = models.DateTimeField(auto_now_add=True)
  #create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='sitestructure_sitestructure_create_user')
  #update_date = models.DateTimeField(auto_now=True)
  #update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='sitestructure_sitestructure_update_user')
  #published = models.BooleanField(default=True)
  #deleted = models.BooleanField(default=False)

  class Meta:
    db_table = 'sitestructure_sitestructure'
    get_latest_by = 'id'
    verbose_name = 'Site Structure Item'
    verbose_name_plural = 'Site Structure Items'
    unique_together = (('parent', 'site_title'),)

  class MPTTMeta:
    pass
    #order_insertion_by = ['level']

  def __str__(self):
    return self.site_title

  #def save(self, *args, **kwargs):
  #  try:
  #    super(SiteStructure, self).save(*args, **kwargs)
  #  except ValidationError:
  #    message.add_message(request, message.ERROR, 'A violdation occured')

  #delete = apps.common.functions.modeltrash
