from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee, System
from django.utils import timezone
from guardian.admin import GuardedModelAdmin
from mptt.admin import MPTTModelAdmin, DraggableMPTTAdmin
from apps.common.classes import DeletedListFilter
from apps.common.actions import trash_selected, restore_selected, publish_selected, unpublish_selected
from django.contrib.admin.actions import delete_selected


# class UserProfileImageInline(admin.StackedInline):
#   model = UserProfileImage
#   extra = 0
#   min_num = 1
#   max_num = 1

class EmployeeAdminAdmin(UserAdmin):
  pass
  # inlines = [UserProfileImageInline,]

class SystemAdminAdmin(UserAdmin):
  pass

admin.site.register(Employee, EmployeeAdminAdmin)
admin.site.register(System, SystemAdminAdmin)
