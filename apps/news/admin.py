from django import forms
from django.contrib import admin
from django.utils import timezone
from guardian.admin import GuardedModelAdmin
from guardian.shortcuts import get_perms
from mptt.admin import MPTTModelAdmin, DraggableMPTTAdmin
from ckeditor.widgets import CKEditorWidget
from apps.common.classes import DeletedListFilter, EditLinkToInlineObject
from apps.common.actions import trash_selected, restore_selected, publish_selected, unpublish_selected
from django.contrib.admin.actions import delete_selected
from .models import News, NewsYear, NewsThumbImage, NewsBannerImage
import uuid
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from apps.sitestructure.models import SiteStructure
from apps.common.classes import ModelAdminOverwrite
from apps.common.functions import has_add_permission, has_change_permission, has_delete_permission, has_add_permission_inline, has_change_permission_inline, has_delete_permission_inline


class NewsInline(EditLinkToInlineObject, admin.TabularInline):
  model = News
  readonly_fields = ('edit_link', )
  fields = ('title', 'edit_link', )
  fk_name = 'parent'
  extra = 0
  min_num = 0
  max_num = 500 

class NewsThumbImageInline(admin.StackedInline):
  model = NewsThumbImage
  extra = 0
  min_num = 0 
  max_num = 1
  fields = ['image','alttext',]
  has_add_permission = has_add_permission_inline
  has_change_permission = has_change_permission_inline
  has_delete_permission = has_delete_permission_inline

class NewsBannerImageInline(admin.StackedInline):
  model = NewsBannerImage
  extra = 0
  min_num = 0
  max_num = 5
  fields = ['image','alttext',]
  has_add_permission = has_add_permission_inline
  has_change_permission = has_change_permission_inline
  has_delete_permission = has_delete_permission_inline

class NewsAdmin(GuardedModelAdmin):
  model = News 
  has_change_permission = has_change_permission
  has_add_permission = has_add_permission
  has_delete_permission = has_delete_permission

  def get_fields(self, request, obj=None):
    if obj:
      return ('title', 'pinned', 'summary', 'body', 'author_date', 'url',)
    else:
      return ('title', 'pinned', 'summary', 'body', 'author_date', 'url',)

  def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['url']
        else:
            return ['url']

  inlines = [NewsThumbImageInline,NewsBannerImageInline]

  def get_list_display(self,request):
    if request.user.has_perm('news.restore_news'):
      return ('title','author_date', 'update_date','update_user','published','deleted')
    else:
      return ('title','author_date', 'update_date','update_user','published',)

  def get_queryset(self, request):
   qs = super().get_queryset(request)
   if request.user.is_superuser:
     return qs
   if request.user.has_perm('news.restore_news'):
     return qs
   return qs.filter(deleted=0)

  def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
          del actions['delete_selected']
        if request.user.has_perm('news.delete_news'):
          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
        if request.user.has_perm('news.restore_news'):
          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
        if request.user.has_perm('news.change_news'):
          actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
          actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
        return actions


  def get_list_filter(self, request):
    if request.user.has_perm('news.restore_news'):
      return (DeletedListFilter,'published','parent')
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

  delete_view = ModelAdminOverwrite.delete_view


class NewsYearAdmin(admin.ModelAdmin):
  def get_fields(self, request, obj=None):
    if obj:
      return ('title', 'yearend', 'parent', 'url',)
    else:
      return ('title', 'yearend', 'parent', 'url',)

  def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['title','parent', 'url']
        else:
            return ['url']

  inlines = [NewsInline,]

  def get_list_display(self,request):
    if request.user.has_perm('news.restore_news'):
      return ('title','update_date','update_user','published','deleted')
    else:
      return ('title','update_date','update_user','published')

  def get_queryset(self, request):
   qs = super().get_queryset(request)
   if request.user.is_superuser:
     return qs
   if request.user.has_perm('news.restore_newsyear'):
     return qs
   return qs.filter(deleted=0)

  def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
          del actions['delete_selected']
        if request.user.has_perm('news.delete_newsyear'):
          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
        if request.user.has_perm('news.restore_newsyear'):
          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
        if request.user.has_perm('news.change_newsyear'):
          actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
          actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
        return actions


  def get_list_filter(self, request):
    if request.user.has_perm('news.restore_newsyear'):
      return (DeletedListFilter,'published')
    else:
      return ('published')

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

admin.site.register(News, NewsAdmin)
admin.site.register(NewsYear, NewsYearAdmin)

#class EditLinkToInlineObject(object):
#    def edit_link(self, instance):
#        url = reverse('admin:%s_%s_change' % (
#            instance._meta.app_label,  instance._meta.model_name),  args=[instance.pk] )
#        if instance.pk:
#            return mark_safe(u'<a href="{u}" >edit</a>'.format(u=url))
#        else:
#            return ''
#
#class BoardBannerImageInline(admin.StackedInline):
#  model = BoardBannerImage
#  extra = 0
#  min_num = 1 
#  max_num = 5
#
#class BoardMemberInline(admin.TabularInline):
#  model = BoardMember
#  extra = 0
#  min_num = 1
#  max_num = 8
#
#class BoardSubPageInline(EditLinkToInlineObject, admin.TabularInline):
#  model = BoardSubPage
#  readonly_fields = ('edit_link', )
#  fields = ('title', 'edit_link', )
#  fk_name = 'parent'
#  extra = 0
#  min_num = 0
#  max_num = 15
#
#  def get_queryset(self, request):
#   qs = super().get_queryset(request)
#   if request.user.is_superuser:
#     return qs
#   if request.user.has_perm('board.restore_board'):
#     return qs
#   return qs.filter(deleted=0)
#
#class BoardAdmin(MPTTModelAdmin, GuardedModelAdmin):
#  def get_fields(self, request, obj=None):
#    if obj:
#      return ('title', 'menu_title', 'body', 'building_location', 'main_phone', 'main_fax', 'mission_statement', 'vision_statement', 'parent','url')
#    else:
#      return ('title', 'menu_title', 'body', 'building_location', 'main_phone', 'main_fax', 'mission_statement', 'vision_statement', 'parent','url')
#
#  inlines = [BoardBannerImageInline, BoardMemberInline, BoardSubPageInline]
#
#  def get_readonly_fields(self, request, obj=None):
#        if obj:
#            return ['title','parent', 'url']
#        else:
#            return ['url']
#
#  def get_list_display(self,request):
#    if request.user.has_perm('board.restore_board'):
#      return ('title','update_date','update_user','published','deleted')
#    else:
#      return ('title','update_date','update_user','published')
#
#  def get_queryset(self, request):
#   qs = super().get_queryset(request)
#   if request.user.is_superuser:
#     return qs
#   if request.user.has_perm('board.restore_board'):
#     return qs
#   return qs.filter(deleted=0)
#
#  def get_actions(self, request):
#        actions = super().get_actions(request)
#        if 'delete_selected' in actions:
#          del actions['delete_selected']
#        if request.user.has_perm('board.delete_board'):    
#          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
#        if request.user.has_perm('board.restore_board'):
#          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
#        if request.user.has_perm('board.change_board'):
#          actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
#          actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
#        return actions
#  
#
#  def get_list_filter(self, request):
#    if request.user.has_perm('board.restore_board'):
#      return (DeletedListFilter,'published')
#    else:
#      return ('published')
#
#  def save_formset(self, request, form, formset, change):
#    instances = formset.save(commit=False)
#    for obj in formset.deleted_objects:
#      obj.delete()
#    for obj in formset.new_objects:
#      obj.create_user = request.user
#      obj.update_user = request.user
#      obj.save()
#    for obj in formset.changed_objects:
#      obj[0].update_user = request.user
#      obj[0].save()
#
#  def save_model(self, request, obj, form, change):
#    if getattr(obj, 'create_user', None) is None:
#      obj.create_user = request.user
#    obj.update_user = request.user
#    super().save_model(request, obj, form, change)
#
#class BoardPrecinctAdmin(MPTTModelAdmin, GuardedModelAdmin):
#  def get_fields(self, request, obj=None):
#    if obj:
#      return ('title',)
#    else:
#      return ('title',)
#
#  def get_readonly_fields(self, request, obj=None):
#        if obj:
#            return []
#        else:
#            return []
#
#  def get_list_display(self,request):
#    if request.user.has_perm('board.restore_boardprecinct'):
#      return ('title','update_date','update_user','published','deleted')
#    else:
#      return ('title','update_date','update_user','published')
#
#  def get_queryset(self, request):
#   qs = super().get_queryset(request)
#   if request.user.is_superuser:
#     return qs
#   if request.user.has_perm('board.restore_boardprecinct'):
#     return qs
#   return qs.filter(deleted=0)
#
#  def get_actions(self, request):
#    actions = super().get_actions(request)
#    if 'delete_selected' in actions:
#      del actions['delete_selected']
#    if request.user.has_perm('board.delete_boardprecinct'):
#      actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
#    if request.user.has_perm('board.restore_boardprecinct'):
#      actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
#    if request.user.has_perm('board.change_boardprecinct'):
#      actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
#      actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
#    return actions
#
#  def get_list_filter(self, request):
#    if request.user.has_perm('board.restore_boardprecinct'):
#      return (DeletedListFilter,'published')
#    else:
#      return ('published')
#
#  def save_model(self, request, obj, form, change):
#    if getattr(obj, 'create_user', None) is None:
#      obj.create_user = request.user
#    obj.update_user = request.user
#    super().save_model(request, obj, form, change)
#
#class BoardSubPageAdmin(GuardedModelAdmin):
#  def get_fields(self, request, obj=None):
#    if obj:
#      return ('title', 'menu_title', 'body', 'parent','url')
#    else:
#      return ('title', 'menu_title', 'body', 'parent','url')
#
#  def get_readonly_fields(self, request, obj=None):
#        if obj:
#            return ['title','parent','url']
#        else:
#            return ['url']
#
#  def get_list_display(self,request):
#    if request.user.has_perm('board.restore_boardsubpage'):
#      return ('title', 'update_date','update_user','published','deleted')
#    else:
#      return ('title', 'update_date','update_user','published')
#
#  def get_queryset(self, request):
#   qs = super().get_queryset(request)
#   if request.user.is_superuser:
#     return qs
#   if request.user.has_perm('board.restore_boardsubpage'):
#     return qs
#   return qs.filter(deleted=0)
#
#  def get_actions(self, request):
#        actions = super().get_actions(request)
#        if 'delete_selected' in actions:
#          del actions['delete_selected']
#        if request.user.has_perm('board.delete_boardsubpage'):
#          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
#        if request.user.has_perm('board.restore_boardsubpage'):
#          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
#        if request.user.has_perm('board.change_boardsubpage'):
#          actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
#          actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
#        return actions
#
#  def get_list_filter(self, request):
#    if request.user.has_perm('board.restore_boardsubpage'):
#      return (DeletedListFilter,'published')
#    else:
#      return ('published',)
#
#  def save_formset(self, request, form, formset, change):
#    instances = formset.save(commit=False)
#    for obj in formset.deleted_objects:
#      obj.delete()
#    for obj in formset.new_objects:
#      obj.create_user = request.user
#      obj.update_user = request.user
#      obj.save()
#    for obj in formset.changed_objects:
#      obj[0].update_user = request.user
#      obj[0].save()
#
#  def save_model(self, request, obj, form, change):
#    if getattr(obj, 'create_user', None) is None:
#      obj.create_user = request.user
#    obj.update_user = request.user
#    super().save_model(request, obj, form, change)
#
#class BoardPolicyAdmin(admin.ModelAdmin):
#  def get_fields(self, request, obj=None):
#    if obj:
#      return ('index', 'title', 'section')
#    else:
#      return ('index', 'title', 'section')
#
#  def get_readonly_fields(self, request, obj=None):
#        if obj:
#            return ['index', 'title', 'section']
#        else:
#            return []
#
#  def get_list_display(self,request):
#    if request.user.has_perm('board.restore_boardpolicy'):
#      return ('get_policy_index' ,'title','update_date','update_user','published','deleted')
#    else:
#      return ('get_policy_index', 'title','update_date','update_user','published')
#  
#  def get_list_display_links(self, request, get_list_display):
#    return ('title',)
#
#  ordering = ('section__section_prefix', 'index',)
#
#  def get_queryset(self, request):
#   qs = super().get_queryset(request)
#   if request.user.is_superuser:
#     return qs
#   if request.user.has_perm('board.restore_boardpolicy'):
#     return qs
#   return qs.filter(deleted=0)
#
#  def get_actions(self, request):
#        actions = super().get_actions(request)
#        if 'delete_selected' in actions:
#          del actions['delete_selected']
#        if request.user.has_perm('board.delete_boardpolicy'):
#          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
#        if request.user.has_perm('board.restore_boardpolicy'):
#          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
#        if request.user.has_perm('board.change_boardpolicy'):
#          actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
#          actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
#        return actions
#
#
#  def get_list_filter(self, request):
#    if request.user.has_perm('board.restore_boardpolicy'):
#      return (DeletedListFilter,'published')
#    else:
#      return ('published')
#
#  def save_formset(self, request, form, formset, change):
#    instances = formset.save(commit=False)
#    for obj in formset.deleted_objects:
#      obj.delete()
#    for obj in formset.new_objects:
#      obj.create_user = request.user
#      obj.update_user = request.user
#      obj.save()
#    for obj in formset.changed_objects:
#      obj[0].update_user = request.user
#      obj[0].save()
#
#  def save_model(self, request, obj, form, change):
#    if getattr(obj, 'create_user', None) is None:
#      obj.create_user = request.user
#    obj.update_user = request.user
#    super().save_model(request, obj, form, change)
#
#class BoardPolicySectionAdmin(admin.ModelAdmin):
#  def get_fields(self, request, obj=None):
#    if obj:
#      return ('title', 'description', 'section_prefix')
#    else:
#      return ('title', 'description', 'section_prefix')
#
#  def get_readonly_fields(self, request, obj=None):
#        if obj:
#            return ['title',]
#        else:
#            return []
#
#  def get_list_display(self,request):
#    if request.user.has_perm('board.restore_boardpolicysection'):
#      return ('title','update_date','update_user','published','deleted')
#    else:
#      return ('title','update_date','update_user','published')
#
#  def get_queryset(self, request):
#   qs = super().get_queryset(request)
#   if request.user.is_superuser:
#     return qs
#   if request.user.has_perm('board.restore_boardpolicysection'):
#     return qs
#   return qs.filter(deleted=0)
#
#  def get_actions(self, request):
#        actions = super().get_actions(request)
#        if 'delete_selected' in actions:
#          del actions['delete_selected']
#        if request.user.has_perm('board.delete_boardpolicysection'):
#          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
#        if request.user.has_perm('board.restore_boardpolicysection'):
#          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
#        if request.user.has_perm('board.change_boardpolicysection'):
#          actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
#          actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
#        return actions
#
#
#  def get_list_filter(self, request):
#    if request.user.has_perm('board.restore_boardpolicysection'):
#      return (DeletedListFilter,'published')
#    else:
#      return ('published')
#
#  def save_formset(self, request, form, formset, change):
#    instances = formset.save(commit=False)
#    for obj in formset.deleted_objects:
#      obj.delete()
#    for obj in formset.new_objects:
#      obj.create_user = request.user
#      obj.update_user = request.user
#      obj.save()
#    for obj in formset.changed_objects:
#      obj[0].update_user = request.user
#      obj[0].save()
#
#  def save_model(self, request, obj, form, change):
#    if getattr(obj, 'create_user', None) is None:
#      obj.create_user = request.user
#    obj.update_user = request.user
#    super().save_model(request, obj, form, change)
#
#class BoardMeetingAdmin(admin.ModelAdmin):
#  def get_fields(self, request, obj=None):
#    if obj:
#      return ('startdate', 'cancelled', 'meeting_type', 'location', 'location_overwrite_title', 'location_overwrite_google_place')
#    else:
#      return ('startdate', 'cancelled', 'meeting_type', 'location', 'location_overwrite_title', 'location_overwrite_google_place')
#
#  def get_readonly_fields(self, request, obj=None):
#        if obj:
#            return []
#        else:
#            return []
#
#  filter_horizontal = ('meeting_type',)
#
#  def get_list_display(self,request):
#    if request.user.has_perm('board.restore_boardmeeting'):
#      return ('startdate','update_date','update_user','published','deleted')
#    else:
#      return ('startdate','update_date','update_user','published')
#
#  def get_list_display_links(self, request, get_list_display):
#    return ('startdate',)
#
#  ordering = ('-startdate',)
#
#  def get_queryset(self, request):
#   qs = super().get_queryset(request)
#   if request.user.is_superuser:
#     return qs
#   if request.user.has_perm('board.restore_boardmeeting'):
#     return qs
#   return qs.filter(deleted=0)
#
#  def get_actions(self, request):
#        actions = super().get_actions(request)
#        if 'delete_selected' in actions:
#          del actions['delete_selected']
#        if request.user.has_perm('board.delete_boardmeeting'):
#          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
#        if request.user.has_perm('board.restore_boardmeeting'):
#          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
#        if request.user.has_perm('board.change_boardmeeting'):
#          actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
#          actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
#        return actions
#
#
#  def get_list_filter(self, request):
#    if request.user.has_perm('board.restore_boardmeeting'):
#      return (DeletedListFilter,'published')
#    else:
#      return ('published')
#
#  def save_formset(self, request, form, formset, change):
#    instances = formset.save(commit=False)
#    for obj in formset.deleted_objects:
#      obj.delete()
#    for obj in formset.new_objects:
#      obj.create_user = request.user
#      obj.update_user = request.user
#      obj.save()
#    for obj in formset.changed_objects:
#      obj[0].update_user = request.user
#      obj[0].save()
#
#  def save_model(self, request, obj, form, change):
#    if getattr(obj, 'create_user', None) is None:
#      obj.create_user = request.user
#    obj.update_user = request.user
#    super().save_model(request, obj, form, change)
#
#class BoardMeetingTypeAdmin(admin.ModelAdmin):
#  def get_fields(self, request, obj=None):
#    if obj:
#      return ('title',)
#    else:
#      return ('title',)
#
#  def get_readonly_fields(self, request, obj=None):
#        if obj:
#            return []
#        else:
#            return []
#
#  def get_list_display(self,request):
#    if request.user.has_perm('board.restore_boardmeetingtype'):
#      return ('title','update_date','update_user','published','deleted')
#    else:
#      return ('title','update_date','update_user','published')
#
#  def get_queryset(self, request):
#   qs = super().get_queryset(request)
#   if request.user.is_superuser:
#     return qs
#   if request.user.has_perm('board.restore_boardmeetingtype'):
#     return qs
#   return qs.filter(deleted=0)
#
#  def get_actions(self, request):
#        actions = super().get_actions(request)
#        if 'delete_selected' in actions:
#          del actions['delete_selected']
#        if request.user.has_perm('board.delete_boardmeetingtype'):
#          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
#        if request.user.has_perm('board.restore_boardmeetingtype'):
#          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
#        if request.user.has_perm('board.change_boardmeetingtype'):
#          actions['publish_selected'] = (publish_selected, 'publish_selected', publish_selected.short_description)
#          actions['unpublish_selected'] = (unpublish_selected, 'unpublish_selected', unpublish_selected.short_description)
#        return actions
#
#
#  def get_list_filter(self, request):
#    if request.user.has_perm('board.restore_boardmeetingtype'):
#      return (DeletedListFilter,'published')
#    else:
#      return ('published')
#
#  def save_formset(self, request, form, formset, change):
#    instances = formset.save(commit=False)
#    for obj in formset.deleted_objects:
#      obj.delete()
#    for obj in formset.new_objects:
#      obj.create_user = request.user
#      obj.update_user = request.user
#      obj.save()
#    for obj in formset.changed_objects:
#      obj[0].update_user = request.user
#      obj[0].save()
#
#  def save_model(self, request, obj, form, change):
#    if getattr(obj, 'create_user', None) is None:
#      obj.create_user = request.user
#    obj.update_user = request.user
#    super().save_model(request, obj, form, change)
#
## Register your models here.
#admin.site.register(Board, BoardAdmin)
#admin.site.register(BoardPrecinct, BoardPrecinctAdmin)
#admin.site.register(BoardSubPage, BoardSubPageAdmin)
#admin.site.register(BoardPolicy, BoardPolicyAdmin)
#admin.site.register(BoardPolicySection, BoardPolicySectionAdmin)
#admin.site.register(BoardMeeting, BoardMeetingAdmin)
#admin.site.register(BoardMeetingType, BoardMeetingTypeAdmin)
