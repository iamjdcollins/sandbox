import os
import shutil
import re
import uuid
from django.conf import settings
from django.contrib.auth import get_permission_codename
from guardian.shortcuts import get_perms
from apps.objects.models import Node
from django.core.cache import cache

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
  try:
    if not os.path.isdir(oldpath) & os.path.isdir(newpath):
      f = open('/tmp/movingfile.txt', 'a')
      f.write('Moving: ' + oldpath + ' To: ' + newpath + '\n')
      f.close()
      shutil.move(oldpath, newpath)
    else:
      try:
        f = open('/tmp/movingfile.txt', 'a')
        f.write('Removing: ' + oldpath + '\n')
        f.close()
        os.rmdir(oldpath)
      except OSError:
        pass
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


# Upload Image Functions

def image_upload_to(instance, filename):
  url = instance.url[1:]
  title = urlclean_objname(instance.title)
  original_file, original_extension = findfileext_media(filename)
  extension = urlclean_fileext(original_extension)
  full_path = '{0}{1}{2}'.format(url,title, extension)
  if not instance.image_file._committed:
    silentdelete_media(settings.MEDIA_ROOT + '/' + full_path)
  return full_path

# Upload File Functions

def file_upload_to(instance, filename):
  url = instance.url[1:]
  title = urlclean_objname(instance.title)
  original_file, original_extension = findfileext_media(filename)
  extension = urlclean_fileext(original_extension)
  full_path = '{0}{1}{2}'.format(url,title, extension)
  if not instance.file_file._committed:
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
  # Set the node type
  self.node_type = 'user'
  # Set the content type
  self.user_type = self._meta.model_name
  self.content_type = self._meta.model_name
  # Save the item
  super(self._meta.model, self).save(*args, **kwargs)
  # Set the user type node
  self.node_type = self.user._meta.model_name
  if urlchanged:
      # Save Children
      for child in self.get_children():
        object = nodefindobject(child)
        object.save()
      # Move Directory
      silentmove_media(settings.MEDIA_ROOT + oldurl, settings.MEDIA_ROOT + self.url)


def pagesave(self, *args, **kwargs):
  f = open('/tmp/movingfile.txt', 'a')
  f.write('Saving Page ' + '\n')
  f.close()
  # Setup New and Deleted Variables
  is_new = self._state.adding
  is_deleted = '_' if self.deleted == True else ''
  # Set UUID if None
  if self.uuid is None:
    self.uuid = uuid.uuid4()
  # Track URL Changes
  urlchanged = False
  parent_url = self.parent.url if self.parent else ''
  oldurl = self.url
  if self.url != urlclean_remdoubleslashes('/' + parent_url + '/' + is_deleted + urlclean_objname(self.title) + '/'): 
    self.url = urlclean_remdoubleslashes('/' + parent_url + '/' + is_deleted + urlclean_objname(self.title) + '/')
    if not is_new:
      urlchanged = True
  # Set the node_title for the node
  self.node_title = self.title
  # Set the node type
  self.node_type = 'page'
  # Set the content type
  self.page_type = self._meta.model_name
  self.content_type = self._meta.model_name
  # if not self.menu_title:
  #   self.menu_title = self.title
  # Save the item
  super(self._meta.model, self).save(*args, **kwargs)
  f = open('/tmp/movingfile.txt', 'a')
  f.write('Page URL Changed: ' + str(urlchanged) + ' From: ' + oldurl + ' To: ' + self.url +  '\n')
  f.close()
  if urlchanged:
      # Save Children
      for child in self.get_children():
        object = nodefindobject(child)
        object.save()
      # Move Directory
      silentmove_media(settings.MEDIA_ROOT + oldurl, settings.MEDIA_ROOT + self.url)
  clearcache(self)

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
  # Set the node type
  self.node_type = 'taxonomy'
  # Set the content type
  self.taxonomy_type = self._meta.model_name
  self.content_type = self._meta.model_name
  # Save the item
  super(self._meta.model, self).save(*args, **kwargs)
  if urlchanged:
      # Save Children
      for child in self.get_children():
        object = nodefindobject(child)
        object.save()
      # Move Directory
      silentmove_media(settings.MEDIA_ROOT + oldurl, settings.MEDIA_ROOT + self.url)
  clearcache(self)

def imagesave(self, *args, **kwargs):
  f = open('/tmp/movingfile.txt', 'a')
  f.write('Saving Image ' + '\n')
  f.close()
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
  if not self.url.startswith(parent_url):
    try:
      self.url = Node.objects.get(pk=self.pk).url
    except Node.DoesNotExist:
      pass
  oldurl = self.url
  if self.url != urlclean_remdoubleslashes('/' + parent_url + '/' + self.URL_PREFIX + '/' + is_deleted + urlclean_objname(self.title) + '/'):
    self.url = urlclean_remdoubleslashes('/' + parent_url + '/' + self.URL_PREFIX + '/' + is_deleted + urlclean_objname(self.title) + '/')
    if not is_new:
      urlchanged = True
  # Move Files
  currentname = None
  newname = None
  if self.image_file:
      currentname = findfileext_media(self.image_file.name)
      newname = image_upload_to(self,currentname[0] + currentname[1])
      currentname = '/'.join (newname.split('/')[:-1]) + '/' + currentname[0] + currentname[1]
      self.image_file.name = newname
      
  # Set the node_title for the node
  self.node_title = self.title
  # Set the node type
  self.node_type = 'image'
  # Set the content type
  self.image_type = self._meta.model_name
  self.content_type = self._meta.model_name
  # Save the item
  super(self._meta.model, self).save(*args, **kwargs)
  f = open('/tmp/movingfile.txt', 'a')
  f.write('Image URL Changed: ' + str(urlchanged) + ' From: ' + oldurl + ' To: ' + self.url +  '\n')
  f.close()
  if urlchanged:
      # Save Children
      for child in self.get_children():
        object = nodefindobject(child)
        object.save()
      # Move Directory
      silentmove_media(settings.MEDIA_ROOT + oldurl, settings.MEDIA_ROOT + self.url)
  # Move File
  if currentname != newname:
    silentmove_media(settings.MEDIA_ROOT + '/' + currentname, settings.MEDIA_ROOT + '/' + newname)
  clearcache(self)

def directoryentrysave(self, *args, **kwargs):
  # Setup New and Deleted Variables
  is_new = self._state.adding
  is_deleted = '_' if self.deleted == True else ''
  #Force Title
  self.title = urlclean_objname(str(self.employee.email).split('@', 1)[0])
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
  if not self.url.startswith(parent_url):
    try:
      self.url = Node.objects.get(pk=self.pk).url
    except Node.DoesNotExist:
      pass
  oldurl = self.url
  if self.url != urlclean_remdoubleslashes('/' + parent_url + '/' + self.URL_PREFIX + '/' + is_deleted + urlclean_objname(self.title) + '/'):
    self.url = urlclean_remdoubleslashes('/' + parent_url + '/' + self.URL_PREFIX + '/' + is_deleted + urlclean_objname(self.title) + '/')
    if not is_new:
      urlchanged = True
  # Set the node_title for the node
  self.node_title = self.title
  # Set the node type
  self.node_type = 'directoryentry'
  # Set the content type
  self.image_type = self._meta.model_name
  self.content_type = self._meta.model_name
  # Save the item
  super(self._meta.model, self).save(*args, **kwargs)
  if urlchanged:
      # Save Children
      for child in self.get_children():
        object = nodefindobject(child)
        object.save()
      # Move Directory
      silentmove_media(settings.MEDIA_ROOT + oldurl, settings.MEDIA_ROOT + self.url)
  clearcache(self)

def linksave(self, *args, **kwargs):
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
  if not self.url.startswith(parent_url):
    try:
      self.url = Node.objects.get(pk=self.pk).url
    except Node.DoesNotExist:
      pass
  oldurl = self.url
  if self.url != urlclean_remdoubleslashes('/' + parent_url + '/' + self.URL_PREFIX + '/' + is_deleted + urlclean_objname(self.title) + '/'):
    self.url = urlclean_remdoubleslashes('/' + parent_url + '/' + self.URL_PREFIX + '/' + is_deleted + urlclean_objname(self.title) + '/')
    if not is_new:
      urlchanged = True
  # Set the node_title for the node
  self.node_title = self.title
  # Set the node type
  self.node_type = 'link'
  # Set the content type
  self.link_type = self._meta.model_name
  self.content_type = self._meta.model_name
  # Save the item
  super(self._meta.model, self).save(*args, **kwargs)
  if urlchanged:
      # Save Children
      for child in self.get_children():
        object = nodefindobject(child)
        object.save()
      # Move Directory
      silentmove_media(settings.MEDIA_ROOT + oldurl, settings.MEDIA_ROOT + self.url)
  clearcache(self)

def filesave(self, *args, **kwargs):
  # Setup New and Deleted Variables
  is_new = self._state.adding
  is_deleted = '_' if self.deleted == True else ''
  #Force Title
  self.title = self.parent.node_title + ' (' + self.file_language.title + ')'
  # Set UUID if None
  if self.uuid is None:
    self.uuid = uuid.uuid4()
  #Force Parent
  if self.PARENT_URL:
    try:
      self.parent = Node.objects.exclude(uuid=self.uuid).get(url=self.PARENT_URL)
    except Node.DoesNotExist:
      pass
  # Related Node matches Parent
  self.related_node = self.parent
  # Track URL Changes
  urlchanged = False
  parent_url = self.parent.url if self.parent else self.PARENT_URL
  if not self.url.startswith(parent_url):
    try:
      self.url = Node.objects.get(pk=self.pk).url
    except Node.DoesNotExist:
      pass
  oldurl = self.url
  if self.url != urlclean_remdoubleslashes('/' + parent_url + '/' + self.URL_PREFIX + '/' + is_deleted + urlclean_objname(self.file_language.title) + '/'):
    self.url = urlclean_remdoubleslashes('/' + parent_url + '/' + self.URL_PREFIX + '/' + is_deleted + urlclean_objname(self.file_language.title) + '/')
    if not is_new:
      urlchanged = True
  # Move Files
  currentname = None
  newname = None
  if self.file_file:
      currentname = findfileext_media(self.file_file.name)
      newname = file_upload_to(self,currentname[0] + currentname[1])
      currentname = '/'.join (newname.split('/')[:-1]) + '/' + currentname[0] + currentname[1]
      self.file_file.name = newname
      
  # Set the node_title for the node
  self.node_title = self.title
  # Set the node type
  self.node_type = 'file'
  # Set the content type
  self.link_type = self._meta.model_name
  self.content_type = self._meta.model_name
  # Save the item
  super(self._meta.model, self).save(*args, **kwargs)
  if urlchanged:
      # Save Children
      for child in self.get_children():
        object = nodefindobject(child)
        object.save()
      # Move Directory
      silentmove_media(settings.MEDIA_ROOT + oldurl, settings.MEDIA_ROOT + self.url)
  # Move File
  if currentname != newname:
    silentmove_media(settings.MEDIA_ROOT + '/' + currentname, settings.MEDIA_ROOT + '/' + newname)
  clearcache(self)

def documentsave(self, *args, **kwargs):
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
  # Related Node matches Parent
  self.related_node = self.parent
  # Track URL Changes
  urlchanged = False
  parent_url = self.parent.url if self.parent else self.PARENT_URL
  if not self.url.startswith(parent_url):
    try:
      self.url = Node.objects.get(pk=self.pk).url
    except Node.DoesNotExist:
      pass
  oldurl = self.url
  if self.url != urlclean_remdoubleslashes('/' + parent_url + '/' + self.URL_PREFIX + '/' + is_deleted + urlclean_objname(self.title) + '/'):
    self.url = urlclean_remdoubleslashes('/' + parent_url + '/' + self.URL_PREFIX + '/' + is_deleted + urlclean_objname(self.title) + '/')
    if not is_new:
      urlchanged = True
  # Set the node_title for the node
  self.node_title = self.title
  # Set the node type
  self.node_type = 'document'
  # Set the content type
  self.link_type = self._meta.model_name
  self.content_type = self._meta.model_name
  # Save the item
  super(self._meta.model, self).save(*args, **kwargs)
  if urlchanged:
      # Save Children
      for child in self.get_children():
        object = nodefindobject(child)
        object.save()
      # Move Directory
      silentmove_media(settings.MEDIA_ROOT + oldurl, settings.MEDIA_ROOT + self.url)
  clearcache(self)  

# Model Inheritance Object
def nodefindobject(node):
  if node.node_type == 'user':
    if node.content_type == 'employee':
      return node.user.employee
    if node.content_type == 'system':
      return node.user.system
  if node.node_type == 'page':
    if node.content_type == 'page':
      return node.page.page
    if node.content_type == 'school':
      return node.page.school
  if node.node_type == 'taxonomy':
    if node.content_type == 'location':
      return node.taxonomy.location
    if node.content_type == 'city':
      return node.taxonomy.city
    if node.content_type == 'state':
      return node.taxonomy.state
    if node.content_type == 'zipcode':
      return node.taxonomy.zipcode
    if node.content_type == 'language':
      return node.taxonomy.language
    if node.content_type == 'translationtype':
      return node.taxonomy.translationtype
    if node.content_type == 'schooltype':
      return node.taxonomy.schooltype
    if node.content_type == 'openenrollmentstatus':
      return node.taxonomy.openenrollmentstatus
  if node.node_type == 'image':
    if node.content_type == 'thumbnail':
      return node.image.thumbnail
    if node.content_type == 'pagebanner':
      return node.image.pagebanner
    if node.content_type == 'contentbanner':
      return node.image.contentbanner
  if node.node_type == 'link':
    if node.content_type == 'resourcelink':
      return node.link.resourcelink
  if node.node_type == 'file':
    if node.content_type == 'file':
      return node.file.file
  if node.node_type == 'document':
    if node.content_type == 'document':
      return node.document.document

# MPTT Tree Functions
def resetchildrentoalphatitle():
  top = Node.objects.filter(node_type='page').get(node_title='Charter Schools')
  children = top.get_children()
  children = children.order_by('node_title')
  parent = children[0]
  parent.move_to(top, position='first-child')
  for child in children[1:]:
    parent = Node.objects.get(pk=parent.pk)
    child = Node.objects.get(pk=child.pk)
    child.move_to(parent, position='right')
    'Moving {0} after {1}'.format(child, parent)
    parent = child
    sleep(1)

# Cache Functions
def clearcache(object):
  pass