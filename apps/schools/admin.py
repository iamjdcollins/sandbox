from django import forms
from django.contrib import admin
from django.utils import timezone
from guardian.admin import GuardedModelAdmin
from mptt.admin import MPTTModelAdmin, DraggableMPTTAdmin
from ckeditor.widgets import CKEditorWidget
from apps.common.classes import DeletedListFilter
from apps.common.actions import trash_selected, restore_selected, publish_selected, unpublish_selected
from django.contrib.admin.actions import delete_selected
from .models import School, SchoolType, SchoolOEStatus, SchoolThumbImage, SchoolBannerImage, SchoolAdmin, SchoolAdminType, SchoolQuickLink
import uuid
from ajax_select import make_ajax_form
from apps.common.functions import has_add_permission, has_change_permission, has_delete_permission, has_add_permission_inline, has_change_permission_inline, has_delete_permission_inline


class SchoolThumbImageInline(admin.StackedInline):
  model = SchoolThumbImage
  extra = 0
  min_num = 1
  max_num = 1

class SchoolBannerImageInline(admin.StackedInline):
  model = SchoolBannerImage
  extra = 0
  min_num = 1 
  max_num = 5

class SchoolAdminInline(admin.TabularInline):
  model = SchoolAdmin
  extra = 0 
  min_num = 1
  max_num = 5

  form = make_ajax_form(SchoolAdmin, {'employee': 'employee'})

class SchoolQuickLinkInline(admin.TabularInline):
  model = SchoolQuickLink.school.through
  extra = 0
  min_num = 0
  max_num = 10
  verbose_name = 'Quick Link'
  verbose_name_plural = 'Quick Links'

class SchoolAdminForm(forms.ModelForm):
  class Meta:
    model = School
    exclude = ['',]
    widgets = {
      'intro_text': CKEditorWidget
    }


class SchoolAdmin(MPTTModelAdmin, GuardedModelAdmin):
  has_add_permission = has_add_permission
  has_change_permission = has_change_permission
  has_delete_permission = has_delete_permission

  def get_fields(self, request, obj=None):
    if obj:
      return ('title', 'menu_title', 'body', 'building_location', 'main_phone', 'main_fax', 'enrollment', 'school_type', 'website_url', 'scc_url', 'boundary_map', 'open_enrollment_status', 'parent','url')
    else:
      return ('title', 'menu_title', 'body', 'building_location', 'main_phone', 'main_fax', 'enrollment', 'school_type', 'website_url', 'scc_url', 'boundary_map', 'open_enrollment_status', 'parent','url')

  inlines = [SchoolAdminInline,SchoolQuickLinkInline,SchoolThumbImageInline,SchoolBannerImageInline,]

  def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['title','parent','url']
        else:
            return ['url']

  def get_list_display(self,request):
    if request.user.has_perm('schools.restore_school'):
      return ('title','update_date','update_user','published','deleted')
    else:
      return ('title','update_date','update_user','published')

#  ordering = ('name',)
  
  def get_queryset(self, request):
   qs = super().get_queryset(request)
   if request.user.is_superuser:
     return qs
   if request.user.has_perm('schools.restore_school'):
     return qs
   return qs.filter(deleted=0)

  def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
          del actions['delete_selected']
        if request.user.has_perm('schools.delete_school'):    
          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
        if request.user.has_perm('schools.restore_school'):
          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
        if request.user.has_perm('schools.change_school'):
          actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
          actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
        return actions
  

  def get_list_filter(self, request):
    if request.user.has_perm('schools.restore_school'):
      return (DeletedListFilter,'school_type','published')
    else:
      return ('school_type','published')

  def save_model(self, request, obj, form, change):
    if getattr(obj, 'create_user', None) is None:
      obj.create_user = request.user
    obj.update_user = request.user
    super().save_model(request, obj, form, change)

class SchoolTypeAdmin(admin.ModelAdmin):
  exclude = ('published', 'deleted', 'create_date', 'create_user', 'update_date', 'update_user',)

  def get_list_display(self,request):
    if request.user.has_perm('schools.restore_schooltype'):
      return ('title','update_date','update_user','published','deleted')
    else:
      return ('title','update_date','update_user','published')

  ordering = ('title',)

  def get_queryset(self, request):
   qs = super().get_queryset(request)
   if request.user.is_superuser:
     return qs
   if request.user.has_perm('schools.restore_schooltype'):
     return qs
   return qs.filter(deleted=0)

  def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
          del actions['delete_selected']
        if request.user.has_perm('schools.trash_schooltype'):
          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
        if request.user.has_perm('schools.restore_schooltype'):
          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
        if request.user.has_perm('schools.change_schooltype'):
          actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
          actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
        return actions

  def get_list_filter(self, request):
    if request.user.has_perm('schools.restore_schooltype'):
      return (DeletedListFilter,'published')
    else:
      return ('published',)

  def save_model(self, request, obj, form, change):
    if getattr(obj, 'create_user', None) is None:
      obj.create_user = request.user
    obj.update_user = request.user
    super().save_model(request, obj, form, change)

class SchoolOEStatusAdmin(admin.ModelAdmin):
  exclude = ('published', 'deleted', 'create_date', 'create_user', 'update_date', 'update_user',)

  def get_list_display(self,request):
    if request.user.has_perm('schools.restore_schooloestatus'):
      return ('title','update_date','update_user','published','deleted')
    else:
      return ('title','update_date','update_user','published')

  ordering = ('title',)

  def get_queryset(self, request):
   qs = super().get_queryset(request)
   if request.user.is_superuser:
     return qs
   if request.user.has_perm('schools.restore_schooloestatus'):
     return qs
   return qs.filter(deleted=0)

  def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.has_perm('schools.delete_schools_schooloestatus'):
          if 'delete_selected' in actions:
            del actions['delete_selected']
        else:
          if 'delete_selected' in actions:
            actions['delete_selected'] = (delete_selected,'delete_selected','Permanently Delete Selected Items')
        if request.user.has_perm('schools.trash_schooloestatus'):
          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
        if request.user.has_perm('schools.restore_schooloestatus'):
          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
        if request.user.has_perm('schools.change_schooloestatus'):
          actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
          actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
        return actions

  def get_list_filter(self, request):
    if request.user.has_perm('schools.restore_schooloestatus'):
      return (DeletedListFilter,'published')
    else:
      return ('published',)

  def save_model(self, request, obj, form, change):
    if getattr(obj, 'create_user', None) is None:
      obj.create_user = request.user
    obj.update_user = request.user
    super().save_model(request, obj, form, change)

class SchoolAdminTypeAdmin(DraggableMPTTAdmin, GuardedModelAdmin):
  def get_fields(self, request, obj=None):
    if obj:
      return ('title',)
    else:
      return ('title',)

  def get_readonly_fields(self, request, obj=None):
        if obj:
            return []
        else:
            return []

  def get_list_display(self,request):
    if request.user.has_perm('schools.restore_schooladmintype'):
      return ('tree_actions','indented_title','update_date','update_user','published','deleted')
    else:
      return ('tree_actions','indented_title','update_date','update_user','published')

  ordering = ('tree_id','level','lft','rght','title')

  def get_queryset(self, request):
   qs = super().get_queryset(request)
   if request.user.is_superuser:
     return qs
   if request.user.has_perm('schools.restore_schooladmintype'):
     return qs
   return qs.filter(deleted=0)

  def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
          del actions['delete_selected']
        if request.user.has_perm('schools.delete_schooladmintype'):
          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
        if request.user.has_perm('schools.restore_schooladmintype'):
          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
        if request.user.has_perm('schools.change_schooladmintype'):
          actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
          actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
        return actions


  def get_list_filter(self, request):
    if request.user.has_perm('schools.restore_schooladmintype'):
      return (DeletedListFilter,'published')
    else:
      return ('published',)

  def save_model(self, request, obj, form, change):
    if getattr(obj, 'create_user', None) is None:
      obj.create_user = request.user
    obj.update_user = request.user
    super().save_model(request, obj, form, change)

class SchoolQuickLinkAdmin(admin.ModelAdmin):
  def get_fields(self, request, obj=None):
    if obj:
      return ('title','url','school')
    else:
      return ('title','url','school')
 
  filter_horizontal = ('school',) 
  
  def get_readonly_fields(self, request, obj=None):
        if obj:
            return []
        else:
            return []

  def get_list_display(self,request):
    if request.user.has_perm('schools.restore_schoolquicklink'):
      return ('title','update_date','update_user','published','deleted')
    else:
      return ('title','update_date','update_user','published')

  ordering = ('title',)

  def get_queryset(self, request):
   qs = super().get_queryset(request)
   if request.user.is_superuser:
     return qs
   if request.user.has_perm('schools.restore_schoolquicklink'):
     return qs
   return qs.filter(deleted=0)

  def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
          del actions['delete_selected']
        if request.user.has_perm('schools.delete_schoolquicklink'):
          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
        if request.user.has_perm('schools.restore_schoolquicklink'):
          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
        if request.user.has_perm('schools.change_schoolquicklink'):
          actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
          actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
        return actions


  def get_list_filter(self, request):
    if request.user.has_perm('schools.restore_schoolquicklink'):
      return (DeletedListFilter,'published')
    else:
      return ('published',)

  def save_model(self, request, obj, form, change):
    if getattr(obj, 'create_user', None) is None:
      obj.create_user = request.user
    obj.update_user = request.user
    super().save_model(request, obj, form, change)

# Register your models here.
admin.site.register(School, SchoolAdmin)
admin.site.register(SchoolType, SchoolTypeAdmin)
admin.site.register(SchoolOEStatus, SchoolOEStatusAdmin)
admin.site.register(SchoolAdminType, SchoolAdminTypeAdmin)
admin.site.register(SchoolQuickLink, SchoolQuickLinkAdmin)
