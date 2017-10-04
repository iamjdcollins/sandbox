from django.conf import settings
from django.db import models
from guardian.shortcuts import assign_perm
from ckeditor.fields import RichTextField
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import Group
import apps.common.functions
from apps.translationlinks.help import TranslationLinkHelp, TranslationLinkTypeHelp
import uuid
from django.contrib.auth import get_permission_codename

# Create your models here.

class TranslationLink(MPTTModel):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False,)
  title = models.CharField(max_length=200, unique=True, help_text=TranslationLinkHelp.title, verbose_name='Language')
  native_language =  models.CharField(max_length=200, unique=True, help_text=TranslationLinkHelp.native_language, verbose_name='Native Language Spelling')
  language_code = models.CharField(max_length=5, unique=True, help_text=TranslationLinkHelp.language_code, verbose_name='Language Code')
  translationlinktype = models.ForeignKey('TranslationLinkType', to_field='uuid', on_delete=models.PROTECT, limit_choices_to={'deleted': False,}, related_name='translationlinks_translationlink_translationlinktype', verbose_name='Translation Link Type')
  parent = TreeForeignKey('self', null=True, blank=True, related_name='translationlinks_translationlink_parent', db_index=True)
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='translationlinks_translationlink_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='translationlinks_translationlink_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'translationlinks_translationlink'
    get_latest_by = 'update_date'
    permissions = (('trash_translationlink', 'Can soft delete translationlink'),('restore_translationlink', 'Can restore translationlink'))
    verbose_name = 'Translation Link'
    verbose_name_plural = 'Translation Links'

  def __str__(self):
    return self.title

  def save(self, *args, **kwargs):
    # Setup New and Deleted Variables
    is_new = self._state.adding
    is_deleted = '_' if self.deleted == True else ''
    # Save the item
    super(self._meta.model, self).save(*args, **kwargs)

  delete = apps.common.functions.modeltrash

class TranslationLinkType(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False,)
  title = models.CharField(max_length=200, unique=True, help_text=TranslationLinkTypeHelp.title, verbose_name='Translation Link Type')
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='translationlinks_translationlinktype_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='translationlinks_translationlinktype_update_user')
  published = models.BooleanField(default=True)
  class Meta:
    db_table = 'translationlinks_translationlinktype'
    get_latest_by = 'update_date'
    permissions = (('trash_translationlinktype', 'Can soft delete translation link type'),('restore_translationlinktype', 'Can restore translation link type'))
    verbose_name = 'Translation Link Type'
    verbose_name_plural = 'Translation Link Types'

  def __str__(self):
    return self.title

  def save(self, *args, **kwargs):
    # Setup New and Deleted Variables
    is_new = self._state.adding
    is_deleted = '_' if self.deleted == True else ''
    # Save the item
    super(self._meta.model, self).save(*args, **kwargs)

  delete = apps.common.functions.modeltrash
