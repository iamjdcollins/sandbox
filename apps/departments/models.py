from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField
from guardian.models import UserObjectPermission
from guardian.shortcuts import assign_perm
from mptt.models import MPTTModel, TreeForeignKey
from mptt.signals import node_moved
from django.contrib.auth.models import Group
import apps.common.functions
from apps.sitestructure.models import SiteStructure
from apps.locations.models import Location
from apps.departments.help import DepartmentHelp, DepartmentBannerImageHelp
from apps.users.models import User
import uuid
from datetime import datetime
from apps.translationlinks.models import TranslationLink
from django.contrib.auth import get_permission_codename

# Create your models here.

def departments_departmentbannerimage_image_upload_to(instance, filename):
  parent_name = apps.common.functions.urlclean_objname(instance.department.title)
  parent_url = instance.department.url[1:]
  uuid = apps.common.functions.urlclean_objname(str(instance.uuid))
  original_file, original_extension = apps.common.functions.findfileext_media(filename)
  extension = apps.common.functions.urlclean_fileext(original_extension)
  full_path = '{0}images/banners/{1}/{2}-banner{3}'.format(parent_url,uuid,parent_name, extension)
  if not instance.image._committed:
    apps.common.functions.silentdelete_media(settings.MEDIA_ROOT + '/' + full_path)
  return full_path

def departments_departmentdocumentfile_file_upload_to(instance, filename):
  title = apps.common.functions.urlclean_objname(instance.document.title)
  url = instance.document.department.url[1:]
  uuid = apps.common.functions.urlclean_objname(str(instance.uuid))
  original_file, original_extension = apps.common.functions.findfileext_media(filename)
  extension = apps.common.functions.urlclean_fileext(original_extension)
  language = apps.common.functions.urlclean_objname(instance.language.language_code)
  full_path = '{0}documents/{1}/{2}-{3}{4}'.format(url,uuid,title,language,extension)
  if not instance.file._committed:
    apps.common.functions.silentdelete_media(settings.MEDIA_ROOT + '/' + full_path)
  return full_path

class Department(SiteStructure):
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False,)
  title = models.CharField(max_length=200, unique=True, help_text=DepartmentHelp.title, verbose_name='Department Name')
  body = RichTextField(null=True, blank=True, help_text=DepartmentHelp.intro_text)
  short_description = models.TextField(max_length=2000, verbose_name='Short Description', null=True, blank=True,)
  building_location = models.ForeignKey(Location, on_delete=models.PROTECT, limit_choices_to={'deleted': False,}, help_text=DepartmentHelp.building_location, related_name='departments_department_building_location')
  main_phone = models.CharField(max_length=11, help_text=DepartmentHelp.main_phone)
  main_fax = models.CharField(max_length=11, help_text=DepartmentHelp.main_fax, null=True, blank=True)
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='departments_department_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='departments_department_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'departments_department'
    get_latest_by = 'update_date'
    permissions = (('trash_department', 'Can soft delete department'),('restore_department', 'Can restore department'))
    verbose_name = 'Department'
    verbose_name_plural = 'Departments'

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
    # if self.parent is not None:
    #   if self.url != apps.common.functions.urlclean_remdoubleslashes('/' + self.parent.url + '/' + apps.common.functions.urlclean_objname(self.title) + '/'):
    #     oldurl = self.url
    #     self.url = apps.common.functions.urlclean_remdoubleslashes('/' + self.parent.url + '/' + apps.common.functions.urlclean_objname(self.title) + '/')
    #     banners = self.departments_departmentbannerimage_department.all()
    #     for banner in banners:
    #       original_name = banner.image.name
    #       original_filename = banner.image.name.split('/')[-1]
    #       original_file, original_extension = apps.common.functions.findfileext_media(original_filename)
    #       banner_extension = apps.common.functions.urlclean_fileext(original_extension)
    #       banner_name = apps.common.functions.urlclean_objname(self.title) + '-banner' + banner_extension
    #       banner_id = apps.common.functions.urlclean_objname(str(banner.uuid))
    #       new_name = '{0}images/banners/{1}/{2}'.format(self.url[1:],banner_id,banner_name)
    #       if original_name != new_name:
    #         apps.common.functions.silentmove_media(settings.MEDIA_ROOT + '/' + original_name, settings.MEDIA_ROOT + '/' + '/'.join(original_name.split('/')[:-1]) + '/'  + banner_name)
    #         banner.image.name = new_name
    #         banner.save()
    #     apps.common.functions.silentmove_media(settings.MEDIA_ROOT + oldurl, settings.MEDIA_ROOT + self.url)
    # else:
    #   if self.url != apps.common.functions.urlclean_remdoubleslashes('/' + apps.common.functions.urlclean_objname(self.title) + '/'):
    #     oldurl = self.url
    #     self.url = apps.common.functions.urlclean_remdoubleslashes('/' + apps.common.functions.urlclean_objname(self.title) + '/')
    #     banners = self.departments_departmentbannerimage_department.all()
    #     for banner in banners:
    #       original_name = banner.image.name
    #       original_filename = banner.image.name.split('/')[-1]
    #       original_file, original_extension = apps.common.functions.findfileext_media(original_filename)
    #       banner_extension = apps.common.functions.urlclean_fileext(original_extension)
    #       banner_name = apps.common.functions.urlclean_objname(self.title) + '-banner' + banner_extension
    #       banner_id = apps.common.functions.urlclean_objname(str(banner.uuid))
    #       new_name = '{0}images/banners/{1}/{2}'.format(self.url[1:],banner_id,banner_name)
    #       if original_name != new_name:
    #         apps.common.functions.silentmove_media(settings.MEDIA_ROOT + '/' + original_name, settings.MEDIA_ROOT + '/' + '/'.join(original_name.split('/')[:-1]) + '/' + banner_name)
    #         banner.image.name = new_name
    #         banner.save()
    #     apps.common.functions.silentmove_media(settings.MEDIA_ROOT + oldurl, settings.MEDIA_ROOT + self.url)
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
    group, created = DepartmentGroup.objects.get_or_create(department_id=self.pk)
    group.name = 'Department: ' + self.title
    group.save()
    assign_perm('change_department', group, self)
    assign_perm('trash_department', group, self)

  delete = apps.common.functions.modeltrash

class DepartmentGroup(Group):
  department = models.OneToOneField('Department', on_delete=models.CASCADE, related_name='departments_departmentgroup_department')

  class Meta:
    db_table = 'departments_departmentgroup'
    verbose_name = 'Department Group'
    verbose_name_plural = 'Department Groups'

class DepartmentBannerImage(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
  department = models.ForeignKey('Department', to_field='uuid', on_delete=models.CASCADE, related_name='departments_departmentbannerimage_department')
  image = models.ImageField(max_length=2000,upload_to=departments_departmentbannerimage_image_upload_to, help_text=DepartmentBannerImageHelp.image)
  alttext = models.CharField(max_length=200, verbose_name='Alternative Text', help_text=DepartmentBannerImageHelp.alttext)
  deleted = models.BooleanField(default=False,)
  create_date = models.DateTimeField(auto_now_add=True,null=True, blank=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='departments_departmentbannerimage_create_user',null=True, blank=True)
  update_date = models.DateTimeField(auto_now=True,null=True, blank=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='departments_departmentbannerimage_update_user',null=True, blank=True)
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'departments_departmentbannerimage'
    get_latest_by = 'update_date'
    permissions = (('trash_departmentbannerimage', 'Can soft delete department banner image'),('restore_departmentbannerimage', 'Can restore department banner image'))
    verbose_name = 'Department Banner Image'
    verbose_name_plural = 'Department Banner Images'

  def __str__(self):
    return self.department.title

  def save(self, *args, **kwargs):
    # Setup New and Deleted Variables
    is_new = self._state.adding
    is_deleted = '_' if self.deleted == True else ''
    # Save the item
    super(self._meta.model, self).save(*args, **kwargs)

  delete = apps.common.functions.modeltrash

class DepartmentStaff(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
  employee = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.PROTECT, related_name='departments_departmentstaff_employee')
  position = models.CharField(max_length=50,null=True, blank=True,help_text="")
  #staff_group = models.CharField(max_length=50,null=True, blank=True,help_text="")
  main_phone = models.CharField(max_length=11, help_text="",null=True,blank=True)
  contact_form = models.BooleanField(default=True)
  department = models.ForeignKey('Department', to_field='uuid', on_delete=models.CASCADE, related_name='departments_departmentstaff_department')
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='departments_departmentstaff_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='departments_departmentstaff_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'departments_departmentstaff'
    get_latest_by = 'update_date'
    permissions = (('trash_departmentstaff', 'Can soft delete department staff'),('restore_departmentstaff', 'Can restore department staff'))
    verbose_name = 'Department Staff'
    verbose_name_plural = 'Department Staff'

  def __str__(self):
    return self.employee.first_name + ' ' + self.employee.last_name

class DepartmentDocument(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
  title = models.CharField(max_length=200, help_text=DepartmentHelp.title, verbose_name='Document Name')
  department = models.ForeignKey('Department', to_field='uuid', on_delete=models.CASCADE, related_name='departments_departmentdocument_department')
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='departments_departmentdocument_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='departments_departmentdocument_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'departments_departmentdocument'
    get_latest_by = 'update_date'
    permissions = (('trash_departmentdocument', 'Can soft delete department document'),('restore_departmentdocument', 'Can restore department document'))
    verbose_name = 'Department Document'
    verbose_name_plural = 'Department Documents'

  def __str__(self):
    return self.department.title + ': ' + self.title

class DepartmentDocumentFile(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
  file = models.FileField(max_length=2000,upload_to=departments_departmentdocumentfile_file_upload_to, help_text="")
  language = models.ForeignKey(TranslationLink, to_field='uuid', on_delete=models.PROTECT, related_name='departments_departmentdocumentfile_language')
  document = models.ForeignKey('DepartmentDocument', to_field='uuid', on_delete=models.CASCADE, related_name='departments_departmentdocumentfile_document')
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='departments_departmentdocumentfile_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='departments_departmentdocumentfile_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'departments_departmentdocumentfile'
    get_latest_by = 'update_date'
    permissions = (('trash_departmentdocumentfile', 'Can soft delete department document file'),('restore_departmentdocumentfile', 'Can restore department document file'))
    verbose_name = 'Department Document File'
    verbose_name_plural = 'Department Documents Files'

  def __str__(self):
    return self.document.department.title + ': ' + self.document.title + '-' + self.language.title

class DepartmentSubPage(SiteStructure):
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False,)
  title = models.CharField(max_length=200, help_text=DepartmentHelp.title, verbose_name='Page Title')
  body = RichTextField(null=True, blank=True, help_text=DepartmentHelp.intro_text)
  building_location = models.ForeignKey(Location, on_delete=models.PROTECT, limit_choices_to={'deleted': False,}, help_text=DepartmentHelp.building_location, related_name='departments_departmentsubpage_building_location', null=True, blank=True)
  main_phone = models.CharField(max_length=11, help_text=DepartmentHelp.main_phone, null=True, blank=True)
  main_fax = models.CharField(max_length=11, help_text=DepartmentHelp.main_fax, null=True, blank=True)
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='departments_departmentsubpage_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='departments_departmentsubpage_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'departments_departmentsubpage'
    get_latest_by = 'update_date'
    permissions = (('trash_departmentsubpage', 'Can soft delete department'),('restore_departmentsubpage', 'Can restore department'))
    verbose_name = 'Department Sub Page'
    verbose_name_plural = 'Department Sub Pages'

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
    # if self.uuid is None:
    #   self.uuid = uuid.uuid4()
    # self.content_type = self.__class__.__name__
    # self.site_title = self.title
    # if not self.menu_title:
    #   self.menu_title = self.title
    # try:
    #   super(DepartmentSubPage, self).save(*args, **kwargs)
    # except ValidationError:
    #   message.add_message(request, message.ERROR, 'A violation occured. The title of the Sub Page my conflicted with another page.')
    group, created = DepartmentGroup.objects.get_or_create(department_id=self.parent.pk)
    group.name = 'Department: ' + self.parent.department.title
    group.save()
    assign_perm('change_departmentsubpage', group, self)
    assign_perm('trash_departmentsubpage', group, self)

  delete = apps.common.functions.modeltrash

class DepartmentSubPageStaff(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
  employee = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.PROTECT, related_name='departments_departmentsubpagestaff_employee')
  position = models.CharField(max_length=50,null=True, blank=True,help_text="")
  main_phone = models.CharField(max_length=11, help_text="",null=True,blank=True)
  contact_form = models.BooleanField(default=True)
  departmentsubpage = models.ForeignKey('DepartmentSubPage', to_field='uuid', on_delete=models.CASCADE, related_name='departments_departmentsubpagestaff_department')
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='departments_departmentsubpagestaff_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='departments_departmentsubpagestaff_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'departments_departmentsubpagestaff'
    get_latest_by = 'update_date'
    permissions = (('trash_departmentsubpagestaff', 'Can soft delete department sub page staff'),('restore_departmentsubpagestaff', 'Can restore department sub page staff'))
    verbose_name = 'Department Sub Page Staff'
    verbose_name_plural = 'Department Sub Page Staff'

  def __str__(self):
    return self.employee.first_name + ' ' + self.employee.last_name
