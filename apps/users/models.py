from django.conf import settings
from django.db import models
import apps.common.functions
import uuid
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_permission_codename
from django.conf import settings
from django.db import models
from guardian.shortcuts import assign_perm
from ckeditor.fields import RichTextField
from django.contrib.auth.models import Group
from treebeard.mp_tree import MP_Node
import apps.common.functions
import uuid
from django.contrib.auth import get_permission_codename
from mptt.models import MPTTModel, TreeForeignKey
from django.conf import settings
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from guardian.shortcuts import assign_perm
from ckeditor.fields import RichTextField
from treebeard.mp_tree import MP_Node
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import Group
import apps.common.functions
import uuid
from django.contrib.auth import get_permission_codename
from apps.objects.models import User

# def users_userprofileimage_image_upload_to(instance, filename):
#   profile_shortname = apps.common.functions.urlclean_objname(str(instance.employee.email).split('@', 1)[0])
#   profile_employee_url = instance.employee.url[1:]
#   profile_id = apps.common.functions.urlclean_objname(str(instance.id))
#   profile_file, profile_extension = apps.common.functions.findfileext_media(filename)
#   profile_extension = apps.common.functions.urlclean_fileext(profile_extension)
#   full_path = '{0}images/profileimage/{1}{2}'.format(profile_employee_url,  profile_shortname, profile_extension)
#   if not instance.image._committed:
#     apps.common.functions.silentdelete_media(settings.MEDIA_ROOT + '/' + full_path)
#   return full_path

class Employee(User):
  PARENT_URL = '/accounts/employees/'

  employee_user_node = models.OneToOneField(User, db_column='employee_user_node', on_delete=models.CASCADE, parent_link=True,)

  class Meta:
    db_table = 'users_employee'
    get_latest_by = 'create_date'
    verbose_name = 'Employee'
    verbose_name_plural = 'Employees'
 
  save = apps.common.functions.usersave
  delete = apps.common.functions.modeltrash

class System(User):
  PARENT_URL = '/accounts/system/'

  system_user_node = models.OneToOneField(User, db_column='system_user_node', on_delete=models.CASCADE, parent_link=True,)

  class Meta:
    db_table = 'users_system'
    get_latest_by = 'create_date'
    verbose_name = 'System'
    verbose_name_plural = 'System'

  save = apps.common.functions.usersave
  delete = apps.common.functions.modeltrash

# class UserProfileImage(models.Model):
#   id = models.AutoField(primary_key=True)
#   uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
#   employee = models.OneToOneField(settings.AUTH_USER_MODEL, to_field='uuid', on_delete=models.CASCADE, related_name='users_userprofileimage_user')
#   image = models.ImageField(max_length=2000,upload_to=users_userprofileimage_image_upload_to, null=True, blank=True)
#   alttext = models.CharField(max_length=200, verbose_name='Alternative Text', null=True, blank=True)

#   class Meta:
#     db_table = 'users_userprofileimage'
#     permissions = (('trash_userprofileimage', 'Can soft delete user profile image'),('restore_userprofileimage', 'Can restore user profile image'))
#     verbose_name = 'User Profile Image'
#     verbose_name_plural = 'User Profile Images'

#   def __str__(self):
#     return self.employee.first_name + ' ' + self.employee.last_name

#   def save(self, *args, **kwargs):
#     # Setup New and Deleted Variables
#     is_new = self._state.adding
#     is_deleted = '_' if self.deleted == True else ''
#     # Save the item
#     super(self._meta.model, self).save(*args, **kwargs)