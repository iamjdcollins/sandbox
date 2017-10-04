from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField
from guardian.models import UserObjectPermission
from guardian.shortcuts import assign_perm
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import Group
import apps.common.functions
from apps.sitestructure.models import SiteStructure
from apps.locations.models import Location, City, State, Zipcode
from apps.locations.help import LocationHelp
from django.contrib.auth import get_permission_codename
import uuid
import pytz
from datetime import datetime
from apps.sitestructure.models import SiteStructure
from apps.users.models import User
from django.contrib.auth import get_permission_codename

# Upload Functions

def newsthumbimage_image_upload_to(instance, filename):
  parent_name = apps.common.functions.urlclean_objname(instance.news.title)
  parent_url = instance.news.url[1:]
  uuid = apps.common.functions.urlclean_objname(str(instance.uuid))
  original_file, original_extension = apps.common.functions.findfileext_media(filename)
  extension = apps.common.functions.urlclean_fileext(original_extension)
  full_path = '{0}images/thumbnails/{1}/{2}-thumbnail{3}'.format(parent_url,uuid,parent_name, extension)
  if not instance.image._committed:
    apps.common.functions.silentdelete_media(settings.MEDIA_ROOT + '/' + full_path)
  return full_path

def newsbannerimage_image_upload_to(instance, filename):
  parent_name = apps.common.functions.urlclean_objname(instance.news.title)
  parent_url = instance.news.url[1:]
  uuid = apps.common.functions.urlclean_objname(str(instance.uuid))
  original_file, original_extension = apps.common.functions.findfileext_media(filename)
  extension = apps.common.functions.urlclean_fileext(original_extension)
  full_path = '{0}images/banners/{1}/{2}-banner{3}'.format(parent_url,uuid,parent_name, extension)
  if not instance.image._committed:
    apps.common.functions.silentdelete_media(settings.MEDIA_ROOT + '/' + full_path)
  return full_path

# Create your models here.

class News(SiteStructure):
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False,)
  title = models.CharField(max_length=200, unique=False, help_text="",)
  body = RichTextField(null=True, blank=True, help_text="",)
  summary = RichTextField(max_length=400, null=True, blank=True, help_text="",)
  pinned = models.BooleanField(default=False,)
  author_date = create_date = models.DateTimeField(default=datetime.now,)
  deleted = models.BooleanField(default=False,)
  create_date = models.DateTimeField(auto_now_add=True,)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='news_news_create_user',)
  update_date = models.DateTimeField(auto_now=True,)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='news_news_update_user',)
  published = models.BooleanField(default=True,)

  class Meta:
    db_table = 'news_news'
    get_latest_by = 'update_date'
    permissions = (('trash_news', 'Can soft delete news'),('restore_news', 'Can restore news'))
    verbose_name = 'News'
    verbose_name_plural = 'News'
    ordering = ['-author_date',]

  def __str__(self):
    return self.title

  def save(self, *args, **kwargs):
    # Setup New and Deleted Variables
    is_new = self._state.adding
    is_deleted = '_' if self.deleted == True else ''
    # Unique to News: Create or find NewsYear
    if self.author_date.month >= 7:
      yearend = self.author_date.year + 1
      yearstring = str(self.author_date.year) + '-' + str(self.author_date.year + 1)[2:]
    else:
      yearend=self.author_date.year
      yearstring = str(self.author_date.year - 1) + '-' + str(self.author_date.year)[2:]
    try:
      newsyear = NewsYear.objects.get(yearend=yearend)
    except NewsYear.DoesNotExist:
      webmaster = User.objects.get(username='webmaster@slcschools.org')
      parent = SiteStructure.objects.get(site_title='News', content_type='Page')
      newsyear = NewsYear(title=yearstring, yearend=yearend, parent=parent, create_user=webmaster, update_user=webmaster)
      newsyear.save()
    self.parent = SiteStructure.objects.get(url=newsyear.url)
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
    #Move files if URL is changing
    if urlchanged:
      apps.common.functions.silentmove_media(settings.MEDIA_ROOT + oldurl, settings.MEDIA_ROOT + self.url)
      try:
        if self.news_newsthumbimage_news:
          self.news_newsthumbimage_news.save()
      except AttributeError:
          pass
      for banner in self.news_newsbannerimage_news.all():
        banner.save()
    #Assign Gaurdian Permissions For Group
    manager, created = Group.objects.get_or_create(name='Manager: News')
    assign_perm('news.add_news', manager)
    assign_perm('news.change_news', manager)
    assign_perm('news.trash_news', manager)
    assign_perm('news.add_news', manager, self)
    assign_perm('news.change_news', manager, self)
    assign_perm('news.trash_news', manager, self)
    group, created = NewsGroup.objects.get_or_create(news_id=self.pk)
    group.name= 'News ' + self.parent.site_title + ': ' + self.title
    group.save()
    assign_perm('news.change_news', group, self)
    assign_perm('news.trash_news', group, self)

  delete = apps.common.functions.modeltrash

class NewsGroup(Group):
  news = models.OneToOneField('News', on_delete=models.CASCADE, related_name='news_newsgroup_news')

  class Meta:
    db_table = 'news_newsgroup'
    permissions = (('trash_newsgroup', 'Can soft delete newsgroup'),('restore_newsgroup', 'Can restore newsgroup'))
    verbose_name = 'News Group'
    verbose_name_plural = 'News Groups'

  def save(self, *args, **kwargs):
    # Setup New and Deleted Variables
    is_new = self._state.adding
    is_deleted = '_' if self.deleted == True else ''
    # Save the item
    super(self._meta.model, self).save(*args, **kwargs)
    manager, created = Group.objects.get_or_create(name='Manager: News')
    group = NewsGroup.objects.get(news_id=self.news.pk)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('add',self._meta), manager)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('change',self._meta), manager)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('trash',self._meta), manager)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('add',self._meta), manager, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('change',self._meta), manager, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('trash',self._meta), manager, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('add',self._meta), group, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('change',self._meta), group, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('trash',self._meta), group, self)

class NewsYear(SiteStructure):
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False,)
  title = models.CharField(max_length=200, unique=True, help_text="",)
  yearend = models.CharField(max_length=4, unique=True, help_text="", blank=True)
  deleted = models.BooleanField(default=False,)
  create_date = models.DateTimeField(auto_now_add=True,)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='news_newsyear_create_user',)
  update_date = models.DateTimeField(auto_now=True,)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='news_newsyear_update_user',)
  published = models.BooleanField(default=True,)

  class Meta:
    db_table = 'news_newsyear'
    get_latest_by = 'update_date'
    permissions = (('trash_newsyear', 'Can soft delete newsyear'),('restore_newsyear', 'Can restore newsyear'))
    verbose_name = 'News Year'
    verbose_name_plural = 'News Years'

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

  delete = apps.common.functions.modeltrash

class NewsThumbImage(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
  news = models.OneToOneField('News', to_field='uuid', on_delete=models.CASCADE, related_name='news_newsthumbimage_news')
  image = models.ImageField(max_length=2000,upload_to=newsthumbimage_image_upload_to, help_text="")
  alttext = models.CharField(max_length=200, verbose_name='Alternative Text', help_text="")
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='news_newsthumbimage_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='news_newsthumbimage_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'news_newsthumbimage'
    get_latest_by = 'update_date'
    permissions = (('trash_newsthumbimage', 'Can soft delete news thumbnail image'),('restore_newsthumbimage', 'Can restore news thumbnail image'))
    verbose_name = 'News Thumbnail Image'
    verbose_name_plural = 'News Thumbnail Images'

  def __str__(self):
    return self.news.title + ' Thumbnail'

  def save(self, *args, **kwargs):
    # Setup New and Deleted Variables
    is_new = self._state.adding
    is_deleted = '_' if self.deleted == True else ''
    if self.image:
      currentname = apps.common.functions.findfileext_media(self.image.name)
      newname = newsthumbimage_image_upload_to(self,currentname[0] + currentname[1])
      currentname = '/'.join (newname.split('/')[:-1]) + '/' + currentname[0] + currentname[1]
      self.image.name = newname
      if currentname != newname:
        apps.common.functions.silentmove_media(settings.MEDIA_ROOT + '/' + currentname, settings.MEDIA_ROOT + '/' + newname)
    # Save the item
    super(self._meta.model, self).save(*args, **kwargs)
    manager, created = Group.objects.get_or_create(name='Manager: News')
    group = NewsGroup.objects.get(news_id=self.news.pk)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('add',self._meta), manager)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('change',self._meta), manager)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('trash',self._meta), manager)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('add',self._meta), manager, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('change',self._meta), manager, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('trash',self._meta), manager, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('add',self._meta), group, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('change',self._meta), group, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('trash',self._meta), group, self)
    
class NewsBannerImage(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
  news = models.ForeignKey('News', to_field='uuid', on_delete=models.CASCADE, related_name='news_newsbannerimage_news')
  image = models.ImageField(max_length=2000,upload_to=newsbannerimage_image_upload_to, help_text="")
  alttext = models.CharField(max_length=200, verbose_name='Alternative Text', help_text="")
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='news_newsbannerimage_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='news_newsbannerimage_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'news_newsbannerimage'
    get_latest_by = 'update_date'
    permissions = (('trash_newsbannerimage', 'Can soft delete news banner image'),('restore_newsbannerimage', 'Can restore news banner image'))
    verbose_name = 'News Banner Image'
    verbose_name_plural = 'News Banner Images'

  def __str__(self):
    return self.news.title + ' Banner'

  def save(self, *args, **kwargs):
    # Setup New and Deleted Variables
    is_new = self._state.adding
    is_deleted = '_' if self.deleted == True else ''
    if self.image:
      currentname = apps.common.functions.findfileext_media(self.image.name)
      newname = newsbannerimage_image_upload_to(self,currentname[0] + currentname[1])
      currentname = '/'.join (newname.split('/')[:-1]) + '/' + currentname[0] + currentname[1]
      self.image.name = newname
      if currentname != newname:
        apps.common.functions.silentmove_media(settings.MEDIA_ROOT + '/' + currentname, settings.MEDIA_ROOT + '/' + newname)
    # Save the item
    super(self._meta.model, self).save(*args, **kwargs)
    manager, created = Group.objects.get_or_create(name='Manager: News')
    group = NewsGroup.objects.get(news_id=self.news.pk)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('add',self._meta), manager)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('change',self._meta), manager)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('trash',self._meta), manager)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('add',self._meta), manager, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('change',self._meta), manager, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('trash',self._meta), manager, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('add',self._meta), group, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('change',self._meta), group, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('trash',self._meta), group, self)