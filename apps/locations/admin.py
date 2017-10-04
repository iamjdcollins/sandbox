from django.contrib import admin
from apps.common.classes import DeletedListFilter
from django.contrib.admin.actions import delete_selected
from .models import Location, City, State, Zipcode

def flag_deleted(modeladmin, request, queryset):
    queryset.update(deleted=1,update_date=timezone.now(),update_user=request.user)
flag_deleted.short_description = "Delete Selected Items"

def flag_notdeleted(modeladmin, request, queryset):
    queryset.update(deleted=0,update_date=timezone.now(),update_user=request.user)
flag_notdeleted.short_description = "Restore Selected Items"

def flag_published(modeladmin, request, queryset):
    queryset.update(published=1,update_date=timezone.now(),update_user=request.user)
flag_published.short_description = "Publish Selected Items"

def flag_unpublished(modeladmin, request, queryset):
    queryset.update(published=0,update_date=timezone.now(),update_user=request.user)
flag_unpublished.short_description = "Unpublish Selected Items"

class LocationAdmin(admin.ModelAdmin):
  exclude = ('published', 'deleted', 'create_date', 'create_user', 'update_date', 'update_user',)

  def get_list_display(self,request):
    if request.user.has_perm('locations.restore_location'):
      return ('location','update_date','update_user','published','deleted')
    else:
      return ('location','update_date','update_user','published')

  ordering = ('location',)

  def get_queryset(self, request):
   qs = super().get_queryset(request)
   if request.user.is_superuser:
     return qs
   if request.user.has_perm('locations.restore_location'):
     return qs
   return qs.filter(deleted=0)

  def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.has_perm('locations.delete_location'):
          if 'delete_selected' in actions:
            del actions['delete_selected']
        else:
          if 'delete_selected' in actions:
            actions['delete_selected'] = (delete_selected,'delete_selected','Permanently Delete Selected Items')
        if request.user.has_perm('locations.trash_location'):
          actions['flag_deleted'] = (flag_deleted,'flag_deleted',flag_deleted.short_description)
        if request.user.has_perm('locations.restore_location'):
          actions['flag_notdeleted'] = (flag_notdeleted,'flag_notdeleted',flag_notdeleted.short_description)
        if request.user.has_perm('locations.change_location'):
          actions['flag_published'] = (flag_published, 'flag_published', flag_published.short_description)
          actions['flag_unpublished'] = (flag_unpublished, 'flag_unpublished', flag_unpublished.short_description)
        return actions

  def get_list_filter(self, request):
    if request.user.has_perm('locations.restore_location'):
      return (DeletedListFilter,'published')
    else:
      return ('published',)

  def save_model(self, request, obj, form, change):
    if getattr(obj, 'create_user', None) is None:
      obj.create_user = request.user
    obj.update_user = request.user
    super().save_model(request, obj, form, change)

class CityAdmin(admin.ModelAdmin):
  exclude = ('published', 'deleted', 'create_date', 'create_user', 'update_date', 'update_user',)

  def get_list_display(self,request):
    if request.user.has_perm('locations.restore_city'):
      return ('city','update_date','update_user','published','deleted')
    else:
      return ('city','update_date','update_user','published')

  ordering = ('city',)

  def get_queryset(self, request):
   qs = super().get_queryset(request)
   if request.user.is_superuser:
     return qs
   if request.user.has_perm('locations.restore_city'):
     return qs
   return qs.filter(deleted=0)

  def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.has_perm('locations.delete_city'):
          if 'delete_selected' in actions:
            del actions['delete_selected']
        else:
          if 'delete_selected' in actions:
            actions['delete_selected'] = (delete_selected,'delete_selected','Permanently Delete Selected Items')
        if request.user.has_perm('locations.trash_city'):
          actions['flag_deleted'] = (flag_deleted,'flag_deleted',flag_deleted.short_description)
        if request.user.has_perm('locations.restore_city'):
          actions['flag_notdeleted'] = (flag_notdeleted,'flag_notdeleted',flag_notdeleted.short_description)
        if request.user.has_perm('locations.change_city'):
          actions['flag_published'] = (flag_published, 'flag_published', flag_published.short_description)
          actions['flag_unpublished'] = (flag_unpublished, 'flag_unpublished', flag_unpublished.short_description)
        return actions

  def get_list_filter(self, request):
    if request.user.has_perm('locations.restore_city'):
      return (DeletedListFilter,'published')
    else:
      return ('published',)

  def save_model(self, request, obj, form, change):
    if getattr(obj, 'create_user', None) is None:
      obj.create_user = request.user
    obj.update_user = request.user
    super().save_model(request, obj, form, change)

class StateAdmin(admin.ModelAdmin):
  exclude = ('published', 'deleted', 'create_date', 'create_user', 'update_date', 'update_user',)

  def get_list_display(self,request):
    if request.user.has_perm('locations.restore_state'):
      return ('state','update_date','update_user','published','deleted')
    else:
      return ('state','update_date','update_user','published')

  ordering = ('state',)

  def get_queryset(self, request):
   qs = super().get_queryset(request)
   if request.user.is_superuser:
     return qs
   if request.user.has_perm('locations.restore_state'):
     return qs
   return qs.filter(deleted=0)

  def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.has_perm('locations.delete_state'):
          if 'delete_selected' in actions:
            del actions['delete_selected']
        else:
          if 'delete_selected' in actions:
            actions['delete_selected'] = (delete_selected,'delete_selected','Permanently Delete Selected Items')
        if request.user.has_perm('locations.trash_state'):
          actions['flag_deleted'] = (flag_deleted,'flag_deleted',flag_deleted.short_description)
        if request.user.has_perm('locations.restore_state'):
          actions['flag_notdeleted'] = (flag_notdeleted,'flag_notdeleted',flag_notdeleted.short_description)
        if request.user.has_perm('locations.change_state'):
          actions['flag_published'] = (flag_published, 'flag_published', flag_published.short_description)
          actions['flag_unpublished'] = (flag_unpublished, 'flag_unpublished', flag_unpublished.short_description)
        return actions

  def get_list_filter(self, request):
    if request.user.has_perm('locations.restore_state'):
      return (DeletedListFilter,'published')
    else:
      return ('published',)

  def save_model(self, request, obj, form, change):
    if getattr(obj, 'create_user', None) is None:
      obj.create_user = request.user
    obj.update_user = request.user
    super().save_model(request, obj, form, change)

class ZipcodeAdmin(admin.ModelAdmin):
  exclude = ('published', 'deleted', 'create_date', 'create_user', 'update_date', 'update_user',)

  def get_list_display(self,request):
    if request.user.has_perm('locations.restore_zipcode'):
      return ('zipcode','update_date','update_user','published','deleted')
    else:
      return ('zipcode','update_date','update_user','published')

  ordering = ('zipcode',)

  def get_queryset(self, request):
   qs = super().get_queryset(request)
   if request.user.is_superuser:
     return qs
   if request.user.has_perm('locations.restore_zipcode'):
     return qs
   return qs.filter(deleted=0)

  def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.has_perm('locations.delete_zipcode'):
          if 'delete_selected' in actions:
            del actions['delete_selected']
        else:
          if 'delete_selected' in actions:
            actions['delete_selected'] = (delete_selected,'delete_selected','Permanently Delete Selected Items')
        if request.user.has_perm('locations.trash_zipcode'):
          actions['flag_deleted'] = (flag_deleted,'flag_deleted',flag_deleted.short_description)
        if request.user.has_perm('locations.restore_zipcode'):
          actions['flag_notdeleted'] = (flag_notdeleted,'flag_notdeleted',flag_notdeleted.short_description)
        if request.user.has_perm('locations.change_zipcode'):
          actions['flag_published'] = (flag_published, 'flag_published', flag_published.short_description)
          actions['flag_unpublished'] = (flag_unpublished, 'flag_unpublished', flag_unpublished.short_description)
        return actions

  def get_list_filter(self, request):
    if request.user.has_perm('locations.restore_zipcode'):
      return (DeletedListFilter,'published')
    else:
      return ('published',)

  def save_model(self, request, obj, form, change):
    if getattr(obj, 'create_user', None) is None:
      obj.create_user = request.user
    obj.update_user = request.user
    super().save_model(request, obj, form, change)

# Register your models here.
admin.site.register(Location, LocationAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Zipcode, ZipcodeAdmin)

