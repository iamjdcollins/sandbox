import os
import shutil
import re
import uuid
from django.conf import settings
from django.contrib.auth import get_permission_codename
from guardian.shortcuts import get_perms
from apps.objects.models import Node

def findfileext_media(media):
  media = media.split('/')[-1:]
  return os.path.splitext(media[0])

def urlclean_fileext(fileext):
  return re.sub('-+','-',re.sub(r'([\s+])','-',re.sub(r'([^.a-z0-9\s-])','',fileext.lower())))

def urlclean_objname(objname):
  return re.sub('-+','-',re.sub(r'([\s+])','-',re.sub(r'([^a-z0-9\s-])','',objname.lower())))

def urlclean_remdoubleslashes(objname):
  return re.sub('/+','/',objname.lower())

def silentdelete_media(media):
  try:
    if os.path.isfile(media):
      os.remove(media)
    elif os.path.isdir(media):
      shutil.rmtree(media, ignore_errors=True)
  except OSError:
    pass

def silentmove_media(oldpath, newpath):
  f = open('/tmp/movingfile.txt', 'a')
  f.write('Moving: ' + oldpath + ' To: ' + newpath + '\n')
  f.close()
  try:
    shutil.move(oldpath, newpath)
  except OSError:
    pass

def has_add_permission(self, request, obj=None):
  if request.path.split('/')[-2:][0] == 'change':
    return False
  if request.user.has_perm(self.model._meta.app_label + '.' + get_permission_codename('add',self.model._meta)):
    return True
  elif obj:
    if get_permission_codename('add',self.model._meta) in get_perms(request.user, obj):
      return True
  return False

def has_change_permission(self, request, obj=None):
  if request.user.has_perm(self.model._meta.app_label + '.' + get_permission_codename('change',self.model._meta)):
    return True
  elif obj:
    if get_permission_codename('change',self.model._meta) in get_perms(request.user, obj):
      return True
  return False

def has_delete_permission(self, request, obj=None):
  if request.user.has_perm(self.model._meta.app_label + '.' + get_permission_codename('trash',self.model._meta)):
    return True
  elif obj:
    if get_permission_codename('trash',self.model._meta) in get_perms(request.user, obj):
      return True
  return False

def has_add_permission_inline(self, request, obj=None):
  if obj == None:
    return True
  if request.user.has_perm(self.model._meta.app_label + '.' + get_permission_codename('add',self.model._meta)):
    return True
  elif obj:
    if get_permission_codename('add',self.model._meta) in get_perms(request.user, obj):
      return True
  return False

def has_change_permission_inline(self, request, obj=None):
  if obj == None:
    return True
  if request.user.has_perm(self.model._meta.app_label + '.' + get_permission_codename('change',self.model._meta)):
    return True
  elif obj:
    if get_permission_codename('change',self.model._meta) in get_perms(request.user, obj):
      return True
  return False

def has_delete_permission_inline(self, request, obj=None):
  if obj == None:
    return True
  if request.user.has_perm(self.model._meta.app_label + '.' + get_permission_codename('trash',self.model._meta)):
    return True
  elif obj:
    if get_permission_codename('trash',self.model._meta) in get_perms(request.user, obj):
      return True
  return False

def modeltrash(self, *args, **kwargs):
    if self.deleted == 0:
      self.deleted = 1;
      self.save()
    else:
      if self.url:
        silentdelete_media(settings.MEDIA_ROOT + self.url)
      super(self._meta.model, self).delete()

def movechildren(self):
  children = self.get_children()
  for child in children:
    if child.content_type == 'Board':
      child.board.save()
    elif child.content_type == 'BoardSubPage':
      child.boardsubpage.save()


# Upload Image Funcations

def thumbimage_image_upload_to(instance, filename):
  url = instance.url[1:]
  title = urlclean_objname(instance.title)
  original_file, original_extension = findfileext_media(filename)
  extension = urlclean_fileext(original_extension)
  full_path = '{0}{1}{2}'.format(url,title, extension)
  if not instance.image._committed:
    silentdelete_media(settings.MEDIA_ROOT + '/' + full_path)
  return full_path

# Save Content Functions

def usersave(self, *args, **kwargs):
  # Setup New and Deleted Variables
  is_new = self._state.adding
  is_deleted = '_' if self.deleted == True else ''
  # Set UUID if None
  if self.uuid is None:
    self.uuid = uuid.uuid4()
  #Force Parent
  if self.PARENT_URL:
    try:
      self.parent = Node.objects.exclude(uuid=self.uuid).get(url=self.PARENT_URL)
    except Node.DoesNotExist:
      pass
  # Track URL Changes
  urlchanged = False
  parent_url = self.parent.url if self.parent else self.PARENT_URL
  if self.url != urlclean_remdoubleslashes('/' + parent_url + '/' +  urlclean_objname(str(self.email).split('@', 1)[0]) + '/'):
    oldurl = self.url 
    self.url = urlclean_remdoubleslashes('/' + parent_url + '/' +  urlclean_objname(str(self.email).split('@', 1)[0]) + '/')
    if not is_new:
      urlchanged = True
  # Set Username
  if self.username:
    self.node_title = self.username
  # Set the user type node
  self.user_type = self._meta.model_name
  # Save the item
  super(self._meta.model, self).save(*args, **kwargs)
  # Set the user type node
  self.node_type = self.user._meta.model_name


def pagesave(self, *args, **kwargs):
  # Setup New and Deleted Variables
  is_new = self._state.adding
  is_deleted = '_' if self.deleted == True else ''
  # Set UUID if None
  if self.uuid is None:
    self.uuid = uuid.uuid4()
  # Track URL Changes
  urlchanged = False
  parent_url = self.parent.url if self.parent else ''
  if self.url != urlclean_remdoubleslashes('/' + parent_url + '/' + is_deleted + urlclean_objname(self.title) + '/'):
    oldurl = self.url 
    self.url = urlclean_remdoubleslashes('/' + parent_url + '/' + is_deleted + urlclean_objname(self.title) + '/')
    if not is_new:
      urlchanged = True
  # Set the node_title for the node
  self.node_title = self.title
  # Set the page type for node
  self.page_type = self._meta.model_name
  #Set the page type node
  self.node_type = 'page'
  # if not self.menu_title:
  #   self.menu_title = self.title
  # Save the item
  super(self._meta.model, self).save(*args, **kwargs)

def taxonomysave(self, *args, **kwargs):
  # Setup New and Deleted Variables
  is_new = self._state.adding
  is_deleted = '_' if self.deleted == True else ''
  # Set UUID if None
  if self.uuid is None:
    self.uuid = uuid.uuid4()
  #Force Parent
  if self.PARENT_URL:
    try:
      self.parent = Node.objects.exclude(uuid=self.uuid).get(url=self.PARENT_URL)
    except Node.DoesNotExist:
      pass
  # Track URL Changes
  urlchanged = False
  parent_url = self.parent.url if self.parent else self.PARENT_URL
  if self.url != urlclean_remdoubleslashes('/' + parent_url + '/' + is_deleted + urlclean_objname(self.title) + '/'):
    oldurl = self.url 
    self.url = urlclean_remdoubleslashes('/' + parent_url + '/' + is_deleted + urlclean_objname(self.title) + '/')
    if not is_new:
      urlchanged = True
  # Set the node_title for the node
  self.node_title = self.title
  # Set the user type node
  self.taxonomy_type = self._meta.model_name
  #Set the page type node
  #Set the page type node
  self.node_type = 'taxonomy'
  # Save the item
  super(self._meta.model, self).save(*args, **kwargs)

def imagesave(self, *args, **kwargs):
  # Setup New and Deleted Variables
  is_new = self._state.adding
  is_deleted = '_' if self.deleted == True else ''
  # Set UUID if None
  if self.uuid is None:
    self.uuid = uuid.uuid4()
  #Force Parent
  if self.PARENT_URL:
    try:
      self.parent = Node.objects.exclude(uuid=self.uuid).get(url=self.PARENT_URL)
    except Node.DoesNotExist:
      pass
  # Track URL Changes
  urlchanged = False
  parent_url = self.parent.url if self.parent else self.PARENT_URL
  if self.url != urlclean_remdoubleslashes('/' + parent_url + '/' + is_deleted + urlclean_objname(self.title) + '/'):
    oldurl = self.url 
    self.url = urlclean_remdoubleslashes('/' + parent_url + '/' + is_deleted + urlclean_objname(self.title) + '/')
    if not is_new:
      urlchanged = True
  # Set the node_title for the node
  self.node_title = self.title
  # Set the user type node
  self.image_type = self._meta.model_name
  #Set the page type node
  #Set the page type node
  self.node_type = 'image'
  # Save the item
  super(self._meta.model, self).save(*args, **kwargs)