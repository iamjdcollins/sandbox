from django.contrib import admin
from django.utils import timezone
from guardian.admin import GuardedModelAdmin
from mptt.admin import MPTTModelAdmin, DraggableMPTTAdmin
from apps.common.classes import DeletedListFilter
from apps.common.actions import trash_selected, restore_selected, publish_selected, unpublish_selected
from django.contrib.admin.actions import delete_selected
from .models import Node

class NodeAdmin(MPTTModelAdmin):
  list_per_page = 100000
  def get_fields(self, request, obj=None):
    if obj:
      return ('node_title', 'parent','url',)
    else:
      return ('node_title', 'parent','url',)

  def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['parent','url',]
        else:
            return ['parent','url',]

  def get_list_display(self,request):
    if request.user.has_perm('sitestructure.restore_sitestricture'):
      return ('node_title','node_type','content_type',)
    else:
      return ('node_title','node_type','content_type',)

# Register your models here.
admin.site.register(Node, NodeAdmin)