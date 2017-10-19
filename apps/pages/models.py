from django.conf import settings
from django.db import models
from guardian.shortcuts import assign_perm
from ckeditor.fields import RichTextField
from django.contrib.auth.models import Group
import apps.common.functions
from apps.objects.models import Page as BasePage
from apps.pages.help import PageHelp
from django.contrib.auth import get_permission_codename
from apps.taxonomy.models import Location, SchoolType, OpenEnrollmentStatus
from apps.images.models import Thumbnail, PageBanner, ContentBanner
from apps.directoryentries.models import SchoolAdministrator

# Create your models here.

class Page(BasePage):
  title = models.CharField(max_length=200, unique=True, help_text='',db_index=True)
  body = RichTextField(null=True, blank=True, help_text=PageHelp.body)

  page_page_node = models.OneToOneField(BasePage, db_column='page_page_node', on_delete=models.CASCADE, parent_link=True,editable=False,)

  class Meta:
    db_table = 'pages_page'
    get_latest_by = 'update_date'
    permissions = (('trash_page', 'Can soft delete page'),('restore_page', 'Can restore page'))
    verbose_name = 'Page'
    verbose_name_plural = 'Pages'

  def __str__(self):
    return self.title

  save = apps.common.functions.pagesave
  delete = apps.common.functions.modeltrash

class School(BasePage):
  
  THUMBNAILS = True
  CONTENTBANNERS = True
  SCHOOLADMINISTRATORS = True

  title = models.CharField(max_length=200, unique=True, help_text='',db_index=True)
  body = RichTextField(null=True, blank=True, help_text='')
  building_location = models.ForeignKey(Location, to_field='location_taxonomy_node', on_delete=models.PROTECT, limit_choices_to={'deleted': False,}, help_text='', related_name='pages_school_building_location')
  main_phone = models.CharField(max_length=11, help_text='')
  main_fax = models.CharField(max_length=11, help_text='')
  enrollment = models.PositiveIntegerField(help_text='')
  schooltype = models.ForeignKey(SchoolType, to_field='schooltype_taxonomy_node', on_delete=models.PROTECT, limit_choices_to={'deleted': False,}, help_text='', related_name='pages_school_schooltype')
  website_url = models.URLField(max_length=2048, help_text='')
  scc_url = models.URLField(max_length=2048, help_text="", null=True, blank=True)
  boundary_map = models.URLField(max_length=2048, help_text='', null=True, blank=True)
  openenrollmentstatus = models.ForeignKey(OpenEnrollmentStatus, to_field='openenrollmentstatus_taxonomy_node', on_delete=models.PROTECT, limit_choices_to={'deleted': False,}, help_text='', related_name='pages_school_openenrollmentstatus')

  school_page_node = models.OneToOneField(BasePage, db_column='school_page_node', on_delete=models.CASCADE, parent_link=True,editable=False,)

  def thumbnails(self):
    return Thumbnail.objects.filter(parent=self.pk)

  def contentbanners(self):
    return ContentBanner.objects.filter(parent=self.pk)

  def schooladministrators(self):
    return SchoolAdministrator.objects.filter(parent=self.pk)

  def resourcelinks(self):
    return self.links_resourcelink_node.all()

  class Meta:
    db_table = 'pages_school'
    get_latest_by = 'update_date'
    permissions = (('trash_school', 'Can soft delete school'),('restore_school', 'Can restore school'))
    verbose_name = 'School'
    verbose_name_plural = 'Schools'

  def __str__(self):
    return self.title

  save = apps.common.functions.pagesave
  delete = apps.common.functions.modeltrash

# class Page(SiteStructure):
#   uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False,)
#   title = models.CharField(max_length=200, unique=True, help_text=PageHelp.title)
#   body = RichTextField(null=True, blank=True, help_text=PageHelp.body)
#   #parent_page = models.ForeignKey('self', to_field='uuid', blank=True, null=True, on_delete=models.PROTECT, limit_choices_to={'deleted': False,}, help_text=PageHelp.parent_page, related_name='pages_page_parent_page')
#   deleted = models.BooleanField(default=False)
#   create_date = models.DateTimeField(auto_now_add=True)
#   create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='pages_page_create_user')
#   update_date = models.DateTimeField(auto_now=True)
#   update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='pages_page_update_user')
#   published = models.BooleanField(default=True)


#   class Meta:
#     db_table = 'pages_page'
#     get_latest_by = 'update_date'
#     permissions = (('trash_page', 'Can soft delete page'),('restore_page', 'Can restore page'))
#     verbose_name = 'Page'
#     verbose_name_plural = 'Pages'

#   def __str__(self):
#     return self.title

#   def save(self, *args, **kwargs):
#     # Setup New and Deleted Variables
#     is_new = self._state.adding
#     is_deleted = '_' if self.deleted == True else ''
#     # Track URL Changes
#     urlchanged = False
#     parent_url = self.parent.url if self.parent else ''
#     if self.url != apps.common.functions.urlclean_remdoubleslashes('/' + parent_url + '/' + is_deleted + apps.common.functions.urlclean_objname(self.title) + '/'):
#       oldurl = self.url 
#       self.url = apps.common.functions.urlclean_remdoubleslashes('/' + parent_url + '/' + is_deleted + apps.common.functions.urlclean_objname(self.title) + '/')
#       if not is_new:
#         urlchanged = True
#     # Set UUID if None
#     if self.uuid is None:
#       self.uuid = uuid.uuid4()
#     # Set the content type for the sitestructure item
#     self.content_type = self.__class__.__name__
#     # Set the site_title for the sitestructure item
#     self.site_title = self.title
#     # Set the menu_title if none for the sitestructure item
#     if not self.menu_title:
#       self.menu_title = self.title
#     # Save the item
#     super(self._meta.model, self).save(*args, **kwargs)
#     group, created = Group.objects.get_or_create(name='Manager: Pages')
#     assign_perm('add_page', group, self)
#     assign_perm('change_page', group, self)
#     assign_perm('trash_page', group, self)
#     group, created = PageGroup.objects.get_or_create(name='Page: ' + self.title, page_id=self.pk)
#     assign_perm('change_page', group, self)
#     assign_perm('trash_page', group, self)

#   delete = apps.common.functions.modeltrash

# class PageGroup(Group):
#   page = models.OneToOneField('Page', on_delete=models.CASCADE, related_name='pages_pagegroup_page')

#   class Meta:
#     db_table = 'pages_pagegroup'
#     verbose_name = 'Page Group'
#     verbose_name_plural = 'Page Groups'
