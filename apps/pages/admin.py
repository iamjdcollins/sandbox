from django.contrib import admin
from django.utils import timezone
from guardian.admin import GuardedModelAdmin
from mptt.admin import MPTTModelAdmin
from adminsortable2.admin import SortableAdminMixin
from ajax_select import make_ajax_form
from apps.common.classes import DeletedListFilter, EditLinkToInlineObject
from apps.common.actions import trash_selected, restore_selected, publish_selected, unpublish_selected
from django.contrib.admin.actions import delete_selected
from .models import Page, School
from apps.images.models import Thumbnail, ContentBanner
from apps.directoryentries.models import SchoolAdministrator
from apps.links.models import ResourceLink
from apps.documents.models import Document
from apps.files.models import File

from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

class ThumbnailInline(admin.TabularInline):
  model = Thumbnail
  fk_name = 'parent'
  fields = ('title','image_file','alttext',)
  extra = 0 
  min_num = 0
  max_num = 1

class ContentBannerInline(admin.TabularInline):
  model = ContentBanner
  fk_name = 'parent'
  fields = ('title','image_file','alttext',)
  extra = 0 
  min_num = 0
  max_num = 5

class SchoolAdministratorInline(admin.TabularInline):
  model = SchoolAdministrator
  fk_name = 'parent'
  fields = ('employee', 'schooladministratortype',)
  extra = 0 
  min_num = 0
  max_num = 5

  form = make_ajax_form(SchoolAdministrator, {'employee': 'employee'})

class ResourceLinkInline(admin.TabularInline):
  model = ResourceLink.related_nodes.through
  fk_name = 'node'
  # fields = ('title','image_file','alttext',)
  extra = 0 
  min_num = 0
  max_num = 50

class DocumentInline(EditLinkToInlineObject, admin.TabularInline):
  model = Document
  fk_name = 'parent'
  readonly_fields = ('edit_link', )
  fields = ('title', 'edit_link', )
  extra = 0 
  min_num = 0
  max_num = 50

class FileInline(admin.TabularInline):
  model = File
  fk_name = 'parent'
  fields = ('file_file', 'file_language')
  extra = 0 
  min_num = 0
  max_num = 50

class PageAdmin(MPTTModelAdmin,GuardedModelAdmin):
  def get_fields(self, request, obj=None):
    if obj:
      return ('title', 'body', 'parent','url')
    else:
      return ('title', 'body', 'parent','url')

  def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['url']
        else:
            return ['url']

  def get_list_display(self,request):
    if request.user.has_perm('pages.restore_page'):
      return ('title','update_date','update_user','published','deleted')
    else:
      return ('title','update_date','update_user','published')

  #ordering = ('url',)
  
  def get_queryset(self, request):
   qs = super().get_queryset(request)
   if request.user.is_superuser:
     return qs
   if request.user.has_perm('pages.restore_page'):
     return qs
   return qs.filter(deleted=0)

  def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
          del actions['delete_selected']
        if request.user.has_perm('pages.trash_page'):    
          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
        if request.user.has_perm('pages.restore_page'):
          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
        if request.user.has_perm('pages.change_page'):
          actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
          actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
        return actions
  

  def get_list_filter(self, request):
    if request.user.has_perm('pages.restore_page'):
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

class SchoolAdmin(MPTTModelAdmin,GuardedModelAdmin):
  inlines = [ThumbnailInline, ContentBannerInline,SchoolAdministratorInline,ResourceLinkInline,DocumentInline,]

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

class ResourceLinkAdmin(MPTTModelAdmin,GuardedModelAdmin):
  def get_fields(self, request, obj=None):
    if obj:
      return ('title', 'link_url','url')
    else:
      return ('title', 'link_url','url')

  def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['url']
        else:
            return ['url']

  def get_list_display(self,request):
    if request.user.has_perm('links.restore_resourcelink'):
      return ('title','update_date','update_user','published','deleted')
    else:
      return ('title','update_date','update_user','published')

  #ordering = ('url',)
  
  def get_queryset(self, request):
   qs = super().get_queryset(request)
   if request.user.is_superuser:
     return qs
   if request.user.has_perm('links.restore_resourcelink'):
     return qs
   return qs.filter(deleted=0)

  def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
          del actions['delete_selected']
        if request.user.has_perm('links.trash_resourcelink'):    
          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
        if request.user.has_perm('links.restore_resourcelink'):
          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
        if request.user.has_perm('links.change_resourcelink'):
          actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
          actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
        return actions
  

  def get_list_filter(self, request):
    if request.user.has_perm('links.restore_resourcelink'):
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

class DocumentAdmin(MPTTModelAdmin,GuardedModelAdmin):
  
  inlines = [FileInline,]

  def get_fields(self, request, obj=None):
    if obj:
      return ('title','url')
    else:
      return ('title', 'url')

  def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['url']
        else:
            return ['url']

  def get_list_display(self,request):
    if request.user.has_perm('documents.restore_document'):
      return ('title','update_date','update_user','published','deleted')
    else:
      return ('title','update_date','update_user','published')

  #ordering = ('url',)
  
  def get_queryset(self, request):
   qs = super().get_queryset(request)
   if request.user.is_superuser:
     return qs
   if request.user.has_perm('documents.restore_document'):
     return qs
   return qs.filter(deleted=0)

  def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
          del actions['delete_selected']
        if request.user.has_perm('documents.trash_document'):
          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
        if request.user.has_perm('documents.restore_document'):
          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
        if request.user.has_perm('documents.change_document'):
          actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
          actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
        return actions
  

  def get_list_filter(self, request):
    if request.user.has_perm('documents.restore_document'):
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

# Register your models here.
admin.site.register(Page, PageAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(ResourceLink,ResourceLinkAdmin)
admin.site.register(Document,DocumentAdmin)