from django.contrib import admin

from django.contrib import admin
from django.utils import timezone
from guardian.admin import GuardedModelAdmin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from mptt.admin import MPTTModelAdmin, DraggableMPTTAdmin
from apps.common.classes import DeletedListFilter
from apps.common.actions import trash_selected, restore_selected, publish_selected, unpublish_selected
from django.contrib.admin.actions import delete_selected
from .models import SiteStructure

class SiteStructureAdmin(DraggableMPTTAdmin):
  def get_fields(self, request, obj=None):
    if obj:
      return ('site_title', 'menu_title', 'menu_item', 'url', 'parent',)#'_position', '_ref_node_id',)
    else:
      return ('site_title', 'menu_title', 'menu_item', 'url', 'parent',)#'_position', '_ref_node_id','create_user')

  def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['url','parent']
        else:
            return ['url','parent']

  def get_list_display(self,request):
    if request.user.has_perm('sitestructure.restore_sitestricture'):
      return ('tree_actions', 'indented_title','content_type',)
    else:
      return ('tree_actions', 'indented_title','content_type',)

#  ordering = ('tree_id','level','lft','rght')
#
#  def get_queryset(self, request):
#   qs = super().get_queryset(request)
#   if request.user.is_superuser:
#     return qs
#   if request.user.has_perm('sitestructure.restore_sitestricture'):
#     return qs
#   return qs.filter(deleted=0)
#
#  def get_actions(self, request):
#        actions = super().get_actions(request)
#        if 'delete_selected' in actions:
#          del actions['delete_selected']
#        if request.user.has_perm('sitestructure.trash_sitestricture'):
#          actions['trash_selected'] = (trash_selected,'trash_selected',trash_selected.short_description)
#        if request.user.has_perm('sitestructure.restore_sitestricture'):
#          actions['restore_selected'] = (restore_selected,'restore_selected',restore_selected.short_description)
#        return actions
#
#
#  def save_model(self, request, obj, form, change):
#    if getattr(obj, 'create_user', None) is None:
#      obj.create_user = request.user
#    obj.update_user = request.user
#    super().save_model(request, obj, form, change)


# Register your models here.
admin.site.register(SiteStructure, SiteStructureAdmin)
