from django import forms
from django.contrib import admin
from django.utils import timezone
from guardian.admin import GuardedModelAdmin
from mptt.admin import MPTTModelAdmin, DraggableMPTTAdmin
from ckeditor.widgets import CKEditorWidget
from apps.common.classes import DeletedListFilter, EditLinkToInlineObject
from apps.common.actions import trash_selected, restore_selected, publish_selected, unpublish_selected
from django.contrib.admin.actions import delete_selected
from .models import Department, DepartmentBannerImage, DepartmentSubPage, DepartmentStaff, DepartmentDocument, DepartmentDocumentFile, DepartmentSubPageStaff
import uuid
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
import logging
from ajax_select import make_ajax_form


logger = logging.getLogger(__name__)

class DepartmentDocumentInline(EditLinkToInlineObject, admin.TabularInline):
  model = DepartmentDocument
  readonly_fields = ('edit_link', )
  fields = ('title', 'edit_link', )
  extra = 0
  min_num = 0
  max_num = 50

class DepartmentDocumentFileInline(admin.TabularInline):
  model = DepartmentDocumentFile
  fields = ('file','language','published')
  extra = 0
  min_num = 1 
  max_num = 50

class DepartmentStaffInline(admin.TabularInline):
  model = DepartmentStaff
  fields = ('employee','position','main_phone','contact_form','published')
  extra = 0
  min_num = 0 
  max_num = 50
 
  form = make_ajax_form(DepartmentStaff, {'employee': 'employee'})

class DepartmentBannerImageInline(admin.StackedInline):
  model = DepartmentBannerImage
  fields = ('image','alttext','published')
  extra = 0
  min_num = 0 
  max_num = 5

  def get_queryset(self, request):
   qs = super().get_queryset(request)
   if request.user.is_superuser:
     return qs
   if request.user.has_perm('departments.restore_department'):
     return qs
   return qs.filter(deleted=0)

class DepartmentSubPageInline(EditLinkToInlineObject, admin.TabularInline):
  model = DepartmentSubPage
  readonly_fields = ('edit_link', )
  fields = ('title', 'edit_link', )
  fk_name = 'parent'
  extra = 0
  min_num = 0 
  max_num = 15

  def get_queryset(self, request):
   qs = super().get_queryset(request)
   if request.user.is_superuser:
     return qs
   if request.user.has_perm('departments.restore_department'):
     return qs
   return qs.filter(deleted=0)

class DepartmentSubPageStaffInline(admin.TabularInline):
  model = DepartmentSubPageStaff
  fields = ('employee','position','main_phone','contact_form','published')
  extra = 0
  min_num = 0
  max_num = 50

  form = make_ajax_form(DepartmentSubPageStaff, {'employee': 'employee'})

class DepartmentAdmin(DraggableMPTTAdmin, GuardedModelAdmin):
  form = make_ajax_form(Department, {'primary_contact': 'employee'})

  def get_fields(self, request, obj=None):
    if obj:
      return ('title', 'menu_title', 'body', 'short_description', 'building_location', 'main_phone', 'main_fax', 'primary_contact', 'parent','url')
    else:
      return ('title', 'menu_title', 'body', 'short_description', 'building_location', 'main_phone', 'main_fax', 'primary_contact', 'parent','url')

  inlines = [DepartmentDocumentInline, DepartmentBannerImageInline,DepartmentSubPageInline,DepartmentStaffInline]

  def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['title','parent','url']
        else:
            return ['url']

  def get_list_display(self,request):
    if request.user.has_perm('departments.restore_department'):
      return ('tree_actions', 'indented_title', 'update_date','update_user','published','deleted')
    else:
      return ('tree_actions', 'indented_title', 'update_date','update_user','published')

  def get_queryset(self, request):
   qs = super().get_queryset(request)
   if request.user.is_superuser:
     return qs
   if request.user.has_perm('departments.restore_department'):
     return qs
   return qs.filter(deleted=0)

  def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
          del actions['delete_selected']
        if request.user.has_perm('departments.delete_department'):    
          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
        if request.user.has_perm('departments.restore_department'):
          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
        if request.user.has_perm('departments.change_department'):
          actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
          actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
        return actions
  

  def get_list_filter(self, request):
    if request.user.has_perm('departments.restore_department'):
      return (DeletedListFilter,'published')
    else:
      return ('published',)
  
  def save_formset(self, request, form, formset, change):
    instances = formset.save(commit=False)
    for obj in formset.deleted_objects:
      obj.delete()
    for obj in formset.new_objects:
      obj.create_user = request.user
      obj.update_user = request.user
      obj.save()
    for obj in formset.changed_objects:
      obj[0].update_user = request.user
      obj[0].save()

  def save_model(self, request, obj, form, change):
    if getattr(obj, 'create_user', None) is None:
      obj.create_user = request.user
    obj.update_user = request.user
    super().save_model(request, obj, form, change)

class DepartmentSubPageAdmin(GuardedModelAdmin):
  def get_fields(self, request, obj=None):
    if obj:
      return ('title', 'menu_title', 'body', 'parent','url')
    else:
      return ('title', 'menu_title', 'body', 'parent','url')

  inlines = [DepartmentSubPageStaffInline, ]

  def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['title','parent','url']
        else:
            return ['url']

  def get_list_display(self,request):
    if request.user.has_perm('departments.restore_departmentsubpage'):
      return ('title', 'update_date','update_user','published','deleted')
    else:
      return ('title', 'update_date','update_user','published')

  def get_queryset(self, request):
   qs = super().get_queryset(request)
   if request.user.is_superuser:
     return qs
   if request.user.has_perm('departments.restore_departmentsubpage'):
     return qs
   return qs.filter(deleted=0)

  def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
          del actions['delete_selected']
        if request.user.has_perm('departments.delete_departmentsubpage'):
          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
        if request.user.has_perm('departments.restore_departmentsubpage'):
          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
        if request.user.has_perm('departments.change_departmentsubpage'):
          actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
          actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
        return actions

  def get_list_filter(self, request):
    if request.user.has_perm('departments.restore_departmentsubpage'):
      return (DeletedListFilter,'published')
    else:
      return ('published',)

  def save_formset(self, request, form, formset, change):
    instances = formset.save(commit=False)
    for obj in formset.deleted_objects:
      obj.delete()
    for obj in formset.new_objects:
      obj.create_user = request.user
      obj.update_user = request.user
      obj.save()
    for obj in formset.changed_objects:
      obj[0].update_user = request.user
      obj[0].save()

  def save_model(self, request, obj, form, change):
    if getattr(obj, 'create_user', None) is None:
      obj.create_user = request.user
    obj.update_user = request.user
    super().save_model(request, obj, form, change)

class DepartmentDocumentAdmin(GuardedModelAdmin):
  def get_fields(self, request, obj=None):
    if obj:
      return ('title',)
    else:
      return ('title',)

  inlines = [DepartmentDocumentFileInline, ]

  def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['title',]
        else:
            return []

  def get_list_display(self,request):
    if request.user.has_perm('departments.restore_departmentdocument'):
      return ('title', 'update_date','update_user','published','deleted')
    else:
      return ('title', 'update_date','update_user','published')

  def get_queryset(self, request):
   qs = super().get_queryset(request)
   if request.user.is_superuser:
     return qs
   if request.user.has_perm('departments.restore_departmentdocument'):
     return qs
   return qs.filter(deleted=0)

  def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
          del actions['delete_selected']
        if request.user.has_perm('departments.delete_departmentdocument'):
          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
        if request.user.has_perm('departments.restore_departmentdocument'):
          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
        if request.user.has_perm('departments.change_departmentdocument'):
          actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
          actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
        return actions

  def get_list_filter(self, request):
    if request.user.has_perm('departments.restore_departmentdocument'):
      return (DeletedListFilter,'published')
    else:
      return ('published',)

  def save_formset(self, request, form, formset, change):
    instances = formset.save(commit=False)
    for obj in formset.deleted_objects:
      obj.delete()
    for obj in formset.new_objects:
      logger.error('New')
      obj.create_user = request.user
      obj.update_user = request.user
      obj.save()
    for obj in formset.changed_objects:
      obj[0].update_user = request.user
      obj[0].save()

  def save_model(self, request, obj, form, change):
    if getattr(obj, 'create_user', None) is None:
      obj.create_user = request.user
    obj.update_user = request.user
    super().save_model(request, obj, form, change)

# Register your models here.
admin.site.register(Department, DepartmentAdmin)
admin.site.register(DepartmentSubPage, DepartmentSubPageAdmin)
admin.site.register(DepartmentDocument, DepartmentDocumentAdmin)
