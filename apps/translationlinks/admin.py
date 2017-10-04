from django.contrib import admin
from django.utils import timezone
from guardian.admin import GuardedModelAdmin
from mptt.admin import MPTTModelAdmin, DraggableMPTTAdmin
from apps.common.classes import DeletedListFilter
from apps.common.actions import trash_selected, restore_selected, publish_selected, unpublish_selected
from django.contrib.admin.actions import delete_selected
from .models import TranslationLink, TranslationLinkType

class TranslationLinkAdmin(DraggableMPTTAdmin, GuardedModelAdmin):
  def get_fields(self, request, obj=None):
    if obj:
      return ('title', 'native_language', 'language_code', 'translationlinktype',)
    else:
      return ('title', 'native_language', 'language_code', 'translationlinktype',)

  def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['title',]
        else:
            return []

  def get_list_display(self,request):
    if request.user.has_perm('translationlinks.restore_translationlink'):
      return ('tree_actions','indented_title','update_date','update_user','published','deleted')
    else:
      return ('tree_actions','indented_title','update_date','update_user','published')

  ordering = ('tree_id','level','lft','rght','title')
  
  def get_queryset(self, request):
   qs = super().get_queryset(request)
   if request.user.is_superuser:
     return qs
   if request.user.has_perm('translationlinks.restore_translationlink'):
     return qs
   return qs.filter(deleted=0)

  def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
          del actions['delete_selected']
        if request.user.has_perm('translationlinks.trash_translationlink'):    
          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
        if request.user.has_perm('translationlinks.restore_translationlink'):
          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
        if request.user.has_perm('translationlinks.change_translationlink'):
          actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
          actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
        return actions
  

  def get_list_filter(self, request):
    if request.user.has_perm('translationlinks.restore_translationlink'):
      return (DeletedListFilter,'published')
    else:
      return ('published',)

  def save_model(self, request, obj, form, change):
    if getattr(obj, 'create_user', None) is None:
      obj.create_user = request.user
    obj.update_user = request.user
    super().save_model(request, obj, form, change)

class TranslationLinkTypeAdmin(GuardedModelAdmin):
  def get_fields(self, request, obj=None):
    if obj:
      return ('title',)
    else:
      return ('title',)

  def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['title',]
        else:
            return []

  def get_list_display(self,request):
    if request.user.has_perm('translationlinktypes.restore_translationlink'):
      return ('title','update_date','update_user','published','deleted')
    else:
      return ('title','update_date','update_user','published')

  ordering = ('title',)

  def get_queryset(self, request):
   qs = super().get_queryset(request)
   if request.user.is_superuser:
     return qs
   if request.user.has_perm('translationlinktypes.restore_translationlink'):
     return qs
   return qs.filter(deleted=0)

  def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
          del actions['delete_selected']
        if request.user.has_perm('translationlinktypes.trash_translationlink'):
          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
        if request.user.has_perm('translationlinktypes.restore_translationlink'):
          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
        if request.user.has_perm('translationlinktypes.change_translationlink'):
          actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
          actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
        return actions


  def get_list_filter(self, request):
    if request.user.has_perm('translationlinktypes.restore_translationlink'):
      return (DeletedListFilter,'published')
    else:
      return ('published',)

  def save_model(self, request, obj, form, change):
    if getattr(obj, 'create_user', None) is None:
      obj.create_user = request.user
    obj.update_user = request.user
    super().save_model(request, obj, form, change)

# Register your models here.
admin.site.register(TranslationLink, TranslationLinkAdmin)
admin.site.register(TranslationLinkType, TranslationLinkTypeAdmin)
