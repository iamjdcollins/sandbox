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
from apps.board.help import BoardHelp, BoardBannerImageHelp, BoardPrecinctHelp, BoardMemberHelp
import uuid
import pytz
from django.contrib.auth import get_permission_codename

# Create your models here.

def board_boardbannerimage_image_upload_to(instance, filename):
  parent_name = apps.common.functions.urlclean_objname(instance.board.title)
  parent_url = instance.board.url[1:]
  uuid = apps.common.functions.urlclean_objname(str(instance.uuid))
  original_file, original_extension = apps.common.functions.findfileext_media(filename)
  extension = apps.common.functions.urlclean_fileext(original_extension)
  full_path = '{0}images/banners/{1}/{2}-banner{3}'.format(parent_url,uuid,parent_name, extension)
  if not instance.image._committed:
    apps.common.functions.silentdelete_media(settings.MEDIA_ROOT + '/' + full_path)
  return full_path

class Board(SiteStructure):
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False,)
  title = models.CharField(max_length=200, unique=True, help_text=BoardHelp.title,)
  body = RichTextField(null=True, blank=True, help_text=BoardHelp.body,)
  mission_statement = models.TextField(max_length=2000, help_text=BoardHelp.title, verbose_name='Mission Statement', null=True, blank=True,)
  vision_statement = models.TextField(max_length=2000, help_text=BoardHelp.title, verbose_name='Vision Statement', null=True, blank=True,)
  building_location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.PROTECT, limit_choices_to={'deleted': False,}, help_text=BoardHelp.building_location, related_name='board_board_building_location')
  main_phone = models.CharField(max_length=11, help_text=BoardHelp.main_phone,)
  main_fax = models.CharField(max_length=11, help_text=BoardHelp.main_fax,)
  deleted = models.BooleanField(default=False,)
  create_date = models.DateTimeField(auto_now_add=True,)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='board_board_create_user',)
  update_date = models.DateTimeField(auto_now=True,)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='board_board_update_user',)
  published = models.BooleanField(default=True,)

  class Meta:
    db_table = 'board_board'
    get_latest_by = 'update_date'
    permissions = (('trash_board', 'Can soft delete board'),('restore_board', 'Can restore board'))
    verbose_name = 'Board'
    verbose_name_plural = 'Board'

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
    #Move files if URL is changing
    if urlchanged:
      apps.common.functions.silentmove_media(settings.MEDIA_ROOT + oldurl, settings.MEDIA_ROOT + self.url)
      apps.common.functions.movechildren(self)
      for banner in self.board_boardbannerimage_board.all():
        banner.save()
    #Assign Gaurdian Permissions For Group
    manager, created = Group.objects.get_or_create(name='Manager: Board')
    assign_perm(self._meta.app_label + '.' + get_permission_codename('add',self._meta), manager)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('change',self._meta), manager)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('trash',self._meta), manager)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('add',self._meta), manager, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('change',self._meta), manager, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('trash',self._meta), manager, self)
    group, created = BoardGroup.objects.get_or_create(board_id=self.pk)
    group.name= 'Board: ' + self.title
    group.save()
    assign_perm(self._meta.app_label + '.' + get_permission_codename('change',self._meta), group, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('trash',self._meta), group, self)

  delete = apps.common.functions.modeltrash

class BoardGroup(Group):
  board = models.OneToOneField('Board', on_delete=models.CASCADE, related_name='board_boardgroup_board')

  class Meta:
    db_table = 'board_boardgroup'
    verbose_name = 'Board Group'
    verbose_name_plural = 'Board Groups'

class BoardBannerImage(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
  board = models.ForeignKey('Board', to_field='uuid', on_delete=models.CASCADE, related_name='board_boardbannerimage_board')
  image = models.ImageField(max_length=2000,upload_to=board_boardbannerimage_image_upload_to, help_text=BoardBannerImageHelp.image)
  alttext = models.CharField(max_length=200, verbose_name='Alternative Text', help_text=BoardBannerImageHelp.alttext)
  deleted = models.BooleanField(default=False,)
  create_date = models.DateTimeField(auto_now_add=True,)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='board_boardbannerimage_create_user',)
  update_date = models.DateTimeField(auto_now=True,)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='board_boardbannerimage_update_user',)
  published = models.BooleanField(default=True,)

  class Meta:
    db_table = 'board_boardbannerimage'
    get_latest_by = 'update_date'
    permissions = (('trash_boardbannerimage', 'Can soft delete board banner image'),('restore_boardbannerimage', 'Can restore board banner image'))
    verbose_name = 'Board Banner Image'
    verbose_name_plural = 'Board Banner Images'

  def __str__(self):
    return self.board.title

  def save(self, *args, **kwargs):
    # Setup New and Deleted Variables
    is_new = self._state.adding
    is_deleted = '_' if self.deleted == True else ''
    if self.image:
      currentname = apps.common.functions.findfileext_media(self.image.name)
      newname = board_boardbannerimage_image_upload_to(self,currentname[0] + currentname[1])
      currentname = '/'.join (newname.split('/')[:-1]) + '/' + currentname[0] + currentname[1]
      self.image.name = newname
      if currentname != newname:
        apps.common.functions.silentmove_media(settings.MEDIA_ROOT + '/' + currentname, settings.MEDIA_ROOT + '/' + newname)
    # Save the item
    super(self._meta.model, self).save(*args, **kwargs)
    manager, created = Group.objects.get_or_create(name='Manager: Board')
    group = BoardGroup.objects.get(board_id=self.board.pk)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('add',self._meta), manager)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('change',self._meta), manager)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('trash',self._meta), manager)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('add',self._meta), manager, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('change',self._meta), manager, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('trash',self._meta), manager, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('add',self._meta), group, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('change',self._meta), group, self)
    assign_perm(self._meta.app_label + '.' + get_permission_codename('trash',self._meta), group, self)

class BoardMember(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
  employee = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.PROTECT, related_name='board_boardmember_employee')
  precinct = models.ForeignKey('BoardPrecinct', to_field='uuid', on_delete=models.PROTECT, related_name='board_boardmember_precinct')
  phone = models.CharField(max_length=11, help_text=BoardMemberHelp.phone)
  street_address = models.CharField(max_length=200, null=True, blank=True, unique=True, help_text=LocationHelp.street_address)
  city = models.ForeignKey(City, null=True, blank=True, to_field='uuid', on_delete=models.PROTECT, related_name='board_boardmember_city', limit_choices_to={'deleted': False,}, help_text=LocationHelp.city)
  state = models.ForeignKey(State, null=True, blank=True, to_field='uuid', on_delete=models.PROTECT, related_name='board_boardmember_state', limit_choices_to={'deleted': False,}, help_text=LocationHelp.state)
  zipcode = models.ForeignKey(Zipcode, null=True, blank=True, to_field='uuid', on_delete=models.PROTECT, related_name='board_boardmember_zipcode', limit_choices_to={'deleted': False,}, help_text=LocationHelp.zipcode)
  board = models.ForeignKey('Board', to_field='uuid', on_delete=models.CASCADE, related_name='board_boardmember_board')

  class Meta:
    db_table = 'board_boardmember'
    permissions = (('trash_boardmember', 'Can soft delete board member'),('restore_boardmember', 'Can restore board member'))
    verbose_name = 'Board Member'
    verbose_name_plural = 'Board Members'

  def __str__(self):
    return self.employee.first_name + ' ' + self.employee.last_name

class BoardPrecinct(MPTTModel):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
  title = models.CharField(max_length=200, unique=True, help_text=BoardPrecinctHelp.title)
  parent = TreeForeignKey('self', null=True, blank=True, related_name='board_boardprecinct_parent', db_index=True)
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='board_boardprecinct_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='board_boardprecinct_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'board_boardprecinct'
    get_latest_by = 'update_date'
    permissions = (('trash_boardprecinct', 'Can soft delete board precinct'),('restore_boardprecinct', 'Can restore board precinct'))
    verbose_name = 'Board Precinct'
    verbose_name_plural = 'Board Precincts'

  def __str__(self):
    return self.title

class BoardSubPage(SiteStructure):
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False,)
  title = models.CharField(max_length=200, help_text="", verbose_name='Page Title')
  body = RichTextField(null=True, blank=True, help_text="")
  building_location = models.ForeignKey(Location, on_delete=models.PROTECT, limit_choices_to={'deleted': False,}, help_text=BoardHelp.building_location, related_name='board_boardsubpage_building_location', null=True, blank=True)
  main_phone = models.CharField(max_length=11, help_text=BoardHelp.main_phone, null=True, blank=True)
  main_fax = models.CharField(max_length=11, help_text=BoardHelp.main_fax, null=True, blank=True)
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='board_boardsubpage_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='board_boardsubpage_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'board_boardsubpage'
    get_latest_by = 'update_date'
    permissions = (('trash_boardsubpage', 'Can soft delete board'),('restore_boardsubpage', 'Can restore board'))
    verbose_name = 'Board Sub Page'
    verbose_name_plural = 'Board Sub Pages'

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
    group, created = BoardGroup.objects.get_or_create(board_id=self.parent.pk)
    group.name = 'Board: ' + self.parent.board.title
    group.save()
    assign_perm('change_boardsubpage', group, self)
    assign_perm('trash_boardsubpage', group, self)

  delete = apps.common.functions.modeltrash

class BoardPolicy(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
  index = models.IntegerField(verbose_name="Policy Number")
  title = models.CharField(max_length=200, unique=True, help_text="",verbose_name="Policy Title")
  section = models.ForeignKey('BoardPolicySection', to_field='uuid', on_delete=models.PROTECT, related_name='board_boardpolicy_section')
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='board_boardpolicy_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='board_boardpolicy_update_user')
  published = models.BooleanField(default=True)

  def get_policy_index(self):
    return '{0}-{1}'.format(self.section.section_prefix, self.index)
  get_policy_index.short_description = 'Policy Index'
  
  def get_section_prefix(self):
    return '{0}'.format(self.section.section_prefix)

  class Meta:
    db_table = 'board_boardpolicy'
    permissions = (('trash_boardpolicy', 'Can soft delete board policy'),('restore_boardpolicy', 'Can restore board policy'))
    verbose_name = 'Board Policy'
    verbose_name_plural = 'Board Policies'

  def __str__(self):
    return self.section.section_prefix + '-' + str(self.index) + ' ' + self.title

class BoardPolicySection(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
  title = models.CharField(max_length=200, unique=True, help_text="",verbose_name="Policy Section Name")
  description = models.CharField(max_length=500,null=True, blank=True,verbose_name="Policy Section Description")
  section_prefix = models.CharField(max_length=1,null=True, blank=True,)
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='board_boardpolicysection_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='board_boardpolicysection_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'board_boardpolicysection'
    permissions = (('trash_boardpolicysection', 'Can soft delete board policy section'),('restore_boardpolicysection', 'Can restore board policy section'))
    verbose_name = 'Board Policy Section'
    verbose_name_plural = 'Board Policy Sections'

  def __str__(self):
    return self.title

class BoardMeeting(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
  startdate = models.DateTimeField(unique=False, verbose_name="Start Date and Time")
  location = models.ForeignKey(Location, default='47edd191-baf4-4cb1-972e-d4a7cd5569ce', to_field='uuid', null=True, blank=True, on_delete=models.PROTECT, limit_choices_to={'deleted': False,}, help_text="", related_name='board_boardmeeting_location')
  location_overwrite_title = models.CharField(max_length=200, null=True, blank=True, help_text="")
  location_overwrite_google_place = models.URLField(max_length=2048, blank=True,null=True, help_text="")
  cancelled = models.BooleanField(default=False)
  meeting_type = models.ManyToManyField('BoardMeetingType', blank=True, related_name='board_boardmeeting_meeting_type')
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='board_boardmeeting_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='board_boardmeeting_update_user')
  published = models.BooleanField(default=True)

  def get_school_year(self):
    if self.startdate.month >= 7:
      return self.startdate.year + 1
    else:
      return self.startdate.year

  class Meta:
    db_table = 'board_boardmeeting'
    permissions = (('trash_boardmeeting', 'Can soft delete board meeting'),('restore_boardmeeting', 'Can restore board meeting'))
    verbose_name = 'Board Meeting'
    verbose_name_plural = 'Board Meetings'
    ordering = ['-startdate']

  def __str__(self):
    return 'Board Meeting: ' + self.startdate.astimezone(pytz.timezone('America/Denver')).strftime("%b. %d, %Y")

class BoardMeetingType(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
  title = models.CharField(max_length=200, unique=True, help_text="",verbose_name="Board Meeting Type")
  deleted = models.BooleanField(default=False)
  create_date = models.DateTimeField(auto_now_add=True)
  create_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='board_boardmeetingtype_create_user')
  update_date = models.DateTimeField(auto_now=True)
  update_user = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.DO_NOTHING, related_name='board_boardmeetingtype_update_user')
  published = models.BooleanField(default=True)

  class Meta:
    db_table = 'board_boardmeetingtype'
    permissions = (('trash_boardmeetingtype', 'Can soft delete board meeting type'),('restore_boardmeetingtype', 'Can restore board meeting type'))
    verbose_name = 'Board Meeting Type'
    verbose_name_plural = 'Board Meeting Types'

  def __str__(self):
    return self.title
