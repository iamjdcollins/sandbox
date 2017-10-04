from django.conf import settings
from django.db import models
from ckeditor.fields import RichTextField
from guardian.models import UserObjectPermission
from guardian.shortcuts import assign_perm
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import Group
import apps.common.functions
from apps.sitestructure.models import SiteStructure
from apps.locations.models import Location
from apps.schools.help import SchoolHelp, SchoolTypeHelp, SchoolOEStatusHelp, SchoolThumbImageHelp, SchoolBannerImageHelp, SchoolAdminTypeHelp
import uuid
from django.contrib.auth import get_permission_codename

# Create your models here.

def schools_schoolthumbimage_image_upload_to(instance, filename):
  parent_name = apps.common.functions.urlclean_objname(instance.school.title)
  parent_url = instance.school.url[1:]
  uuid = apps.common.functions.urlclean_objname(str(instance.uuid))
  original_file, original_extension = apps.common.functions.findfileext_media(filename)
  extension = apps.common.functions.urlclean_fileext(original_extension)
  full_path = '{0}images/thumbnails/{1}/{2}-thumbnail{3}'.format(parent_url,uuid,parent_name, extension)
  if not instance.image._committed:
    apps.common.functions.silentdelete_media(settings.MEDIA_ROOT + '/' + full_path)
  return full_path

def schools_schoolbannerimage_image_upload_to(instance, filename):
  parent_name = apps.common.functions.urlclean_objname(instance.school.title)
  parent_url = instance.school.url[1:]
  uuid = apps.common.functions.urlclean_objname(str(instance.uuid))
  original_file, original_extension = apps.common.functions.findfileext_media(filename)
  extension = apps.common.functions.urlclean_fileext(original_extension)
  full_path = '{0}images/banners/{1}/{2}-banner{3}'.format(parent_url,uuid,parent_name, extension)
  if not instance.image._committed:
    apps.common.functions.silentdelete_media(settings.MEDIA_ROOT + '/' + full_path)
  return full_path

class School(SiteStructure):
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False,)
  title = models.CharField(max_length=200, unique=True, help_text=SchoolHelp.title)
  body = RichTextField(null=True, blank=True, help_text=SchoolHelp.intro_text)
  building_location = models.ForeignKey(Location, on_delete=models.PROTECT, limit_choices_to={'deleted': False,}, help_text=SchoolHelp.building_location, related_name='schools_school_building_location')
  main_phone = models.CharField(max_length=11, help_text=SchoolHelp.main_phone)
  main_fax = models.CharField(max_length=11, help_text=SchoolHelp.main_fax)
  enrollment = models.PositiveIntegerField(help_text=SchoolHelp.enrollment)
  school_type = models.ForeignKey('SchoolType', to_field='uuid', on_delete=models.PROTECT, limit_choices_to={'deleted': False,}, help_text=SchoolHelp.school_type, related_name='schools_school_school_type')
  website_url = models.URLField(max_length=2048, help_text=SchoolHelp.website_url)
  scc_url = models.URLField(max_length=2048, help_text="", null=True, blank=True)
  boundary_map = models.URLField(max_length=2048, help_text=SchoolHelp.boundary_map, null=True, blank=True)
  open_enrollment_status = models.ForeignKey('SchoolOEStatus', to_field='uuid', on_delete=models.PROTECT, limit_choices_to={'deleted': False,}, help_text=SchoolHelp.open_enrollment_status, related_name='schools_school_open_enrollment_status')
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='schools_school_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='schools_school_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'schools_school'
    get_latest_by = 'update_date'
    permissions = (('trash_school', 'Can soft delete school'),('restore_school', 'Can restore school'))
    verbose_name = 'School'
    verbose_name_plural = 'Schools'

  def __str__(self):
    return self.title

  def save(self, *args, **kwargs):
    # Setup New and Deleted Variables
    is_new = self._state.adding
    is_deleted = '_' if self.deleted == True else ''
    # Track URL Changes
    urlchanged = False
    parent_url = self.parent.url if self.parent else ''
    if self.url != apps.common.functions.urlclean_remdoubleslashes('/' + parent_url + '/' + is_deleted + apps.common.functions.urlclean_objname(self.title) + '/'):
      oldurl = self.url 
      self.url = apps.common.functions.urlclean_remdoubleslashes('/' + parent_url + '/' + is_deleted + apps.common.functions.urlclean_objname(self.title) + '/')
      if not is_new:
        urlchanged = True
    # Set UUID if None
    if self.uuid is None:
      self.uuid = uuid.uuid4()
    # Set the content type for the sitestructure item
    self.content_type = self.__class__.__name__
    # Set the site_title for the sitestructure item
    self.site_title = self.title
    # Set the menu_title if none for the sitestructure item
    if not self.menu_title:
      self.menu_title = self.title
    # Save the item
    super(self._meta.model, self).save(*args, **kwargs)
    group, created = SchoolGroup.objects.get_or_create(name='School: ' + self.title, school_id=self.pk)
    assign_perm('change_school', group, self)
    assign_perm('trash_school', group, self)

  delete = apps.common.functions.modeltrash

class SchoolGroup(Group):
  school = models.OneToOneField('School', on_delete=models.CASCADE, related_name='schools_schoolgroup_school')

  class Meta:
    db_table = 'schools_schoolgroup'
    verbose_name = 'School Group'
    verbose_name_plural = 'School Groups'

class SchoolType(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
  title = models.CharField(max_length=200, unique=True, help_text=SchoolTypeHelp.title)
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='schools_schooltype_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='schools_schooltype_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'schools_schooltype'
    get_latest_by = 'update_date'
    permissions = (('trash_schooltype', 'Can soft delete school type'),('restore_schooltype', 'Can restore school type'))
    verbose_name = 'School Type'
    verbose_name_plural = 'School Types'

  def __str__(self):
    return self.title


class SchoolOEStatus(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
  title = models.CharField(max_length=200, unique=True, help_text=SchoolOEStatusHelp.title)
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='schools_schooloestatus_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='schools_schooloestatus_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'schools_schooloestatus'
    get_latest_by = 'update_date'
    permissions = (('trash_schooloestatus', 'Can soft delete school open enrollment status'),('restore_schooloestatus', 'Can restore school open enrollment status'))
    verbose_name = 'School Open Enrollment Status'
    verbose_name_plural = 'School Open Enrollment Statuses'

  def __str__(self):
    return self.title

class SchoolThumbImage(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
  school = models.OneToOneField('School', to_field='uuid', on_delete=models.CASCADE, related_name='schools_schoolthumbimage_school')
  image = models.ImageField(max_length=2000,upload_to=schools_schoolthumbimage_image_upload_to, help_text=SchoolThumbImageHelp.image)
  alttext = models.CharField(max_length=200, verbose_name='Alternative Text', help_text=SchoolThumbImageHelp.alttext)
  #deleted = models.BooleanField(default=False)
  #create_date = models.DateTimeField(auto_now_add=True)
  #create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='schools_schoolthumbimage_create_user')
  #update_date = models.DateTimeField(auto_now=True)
  #update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='schools_schoolthumbimage_update_user')
  #published = models.BooleanField(default=True)

  class Meta:
    db_table = 'schools_schoolthumbimage'
    get_latest_by = 'update_date'
    permissions = (('trash_schoolthumbimage', 'Can soft delete school thumbnail image'),('restore_schoolthumbimage', 'Can restore school thumbnail image'))
    verbose_name = 'School Thumbnail Image'
    verbose_name_plural = 'School Thumbnail Images'

  def __str__(self):
    return self.school.title

  def save(self, *args, **kwargs):
    # Setup New and Deleted Variables
    is_new = self._state.adding
    is_deleted = '_' if self.deleted == True else ''
    # Save the item
    super(self._meta.model, self).save(*args, **kwargs)

class SchoolBannerImage(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
  school = models.ForeignKey('School', to_field='uuid', on_delete=models.CASCADE, related_name='schools_schoolbannerimage_school')
  image = models.ImageField(max_length=2000,upload_to=schools_schoolbannerimage_image_upload_to, help_text=SchoolBannerImageHelp.image)
  alttext = models.CharField(max_length=200, verbose_name='Alternative Text', help_text=SchoolBannerImageHelp.alttext)
  #deleted = models.BooleanField(default=False)
  #create_date = models.DateTimeField(auto_now_add=True)
  #create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='schools_schoolbannerimage_create_user')
  #update_date = models.DateTimeField(auto_now=True)
  #update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='schools_schoolbannerimage_update_user')
  #published = models.BooleanField(default=True)

  class Meta:
    db_table = 'schools_schoolbannerimage'
    get_latest_by = 'update_date'
    permissions = (('trash_schoolbannerimage', 'Can soft delete school banner image'),('restore_schoolbannerimage', 'Can restore school banner image'))
    verbose_name = 'School Banner Image'
    verbose_name_plural = 'School Banner Images'

  def __str__(self):
    return self.school.title

  def save(self, *args, **kwargs):
    # Setup New and Deleted Variables
    is_new = self._state.adding
    is_deleted = '_' if self.deleted == True else ''
    # Save the item
    super(self._meta.model, self).save(*args, **kwargs)

class SchoolAdmin(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
  employee = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.PROTECT, related_name='schools_schooladmin_employee')
  admin_type = models.ForeignKey('SchoolAdminType', to_field='uuid', on_delete=models.PROTECT, related_name='schools_schooladmin_admin_type')
  phone = models.CharField(max_length=11, help_text="")
  school = models.ForeignKey('School', to_field='uuid', on_delete=models.CASCADE, related_name='schools_schooladmin_school')
  #deleted = models.BooleanField(default=False)
  #create_date = models.DateTimeField(auto_now_add=True)
  #create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='schools_schooladmin_create_user')
  #update_date = models.DateTimeField(auto_now=True)
  #update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='schools_schooladmin_update_user')
  #published = models.BooleanField(default=True)

  class Meta:
    db_table = 'schools_schooladmin'
    get_latest_by = 'update_date'
    permissions = (('trash_schooladmin', 'Can soft delete school admin'),('restore_schooladmin', 'Can restore school admin'))
    verbose_name = 'School Administrator'
    verbose_name_plural = 'School Administrators'

  def __str__(self):
    return self.employee.first_name + ' ' + self.employee.last_name

class SchoolAdminType(MPTTModel):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
  title = models.CharField(max_length=200, unique=True, help_text=SchoolAdminTypeHelp.title)
  parent = TreeForeignKey('self', null=True, blank=True, related_name='schools_schooladmintype_parent', db_index=True)
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='schools_schooladmintype_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='schools_schooladmintype_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'schools_schooladmintype'
    get_latest_by = 'update_date'
    permissions = (('trash_schooladmintype', 'Can soft delete school admin type'),('restore_schooladmintype', 'Can restore school admin type'))
    verbose_name = 'School Administration Type'
    verbose_name_plural = 'School Administration Types'

  def __str__(self):
    return self.title

class SchoolQuickLink(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
  title = models.CharField(max_length=200, unique=True, help_text="")
  url = models.URLField(max_length=2048, help_text="",)
  school = models.ManyToManyField('School', related_name='schools_schoolquicklink_school')
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='schools_schoolquicklink_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='schools_schoolquicklink_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'schools_schoolquicklink'
    get_latest_by = 'update_date'
    permissions = (('trash_schoolquicklink', 'Can soft delete school quicklink'),('restore_schoolquicklink', 'Can restore school quicklink'))
    verbose_name = u'School Quick Link'
    verbose_name_plural = u'School Quick Links'

  def __str__(self):
    return self.title
