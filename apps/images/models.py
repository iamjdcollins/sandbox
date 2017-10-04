from django.db import models
import apps.common.functions
from apps.objects.models import Image

class Thumbnail(Image):
  title = models.CharField(max_length=200, unique=True, help_text='')
  image_file = models.ImageField(max_length=2000, verbose_name='Image', help_text='')
  alttext = models.CharField(max_length=200, verbose_name='Alternative Text', help_text='')

  thumbnail_image_node = models.OneToOneField(Image, db_column='thumbnail_image_node', on_delete=models.CASCADE, parent_link=True,)

  class Meta:
    db_table = 'images_thumbnail'
    get_latest_by = 'update_date'
    permissions = (('trash_thumbnail', 'Can soft delete thumbnail'),('restore_thumbnail', 'Can restore thumbnail'))
    verbose_name = 'Thumbnail'
    verbose_name_plural = 'Thumbnails'

  def __str__(self):
    return self.title

  save = apps.common.functions.imagesave
  delete = apps.common.functions.modeltrash

class PageBanner(Image):
  title = models.CharField(max_length=200, unique=True, help_text='')
  image_file = models.ImageField(max_length=2000, verbose_name='Image', help_text='')
  alttext = models.CharField(max_length=200, verbose_name='Alternative Text', help_text='')

  pagebanner_image_node = models.OneToOneField(Image, db_column='pagebanner_image_node', on_delete=models.CASCADE, parent_link=True,)

  class Meta:
    db_table = 'images_pagebanner'
    get_latest_by = 'update_date'
    permissions = (('trash_pagebanner', 'Can soft delete page banner'),('restore_fullbanner', 'Can restore page banner'))
    verbose_name = 'Page Banner'
    verbose_name_plural = 'Page Banners'

  def __str__(self):
    return self.title

  save = apps.common.functions.imagesave
  delete = apps.common.functions.modeltrash

class ContentBanner(Image):
  title = models.CharField(max_length=200, unique=True, help_text='')
  image_file = models.ImageField(max_length=2000, verbose_name='Image', help_text='')
  alttext = models.CharField(max_length=200, verbose_name='Alternative Text', help_text='')

  contentbanner_image_node = models.OneToOneField(Image, db_column='contentbanner_image_node', on_delete=models.CASCADE, parent_link=True,)

  class Meta:
    db_table = 'images_pagebanner'
    get_latest_by = 'update_date'
    permissions = (('trash_pagebanner', 'Can soft delete page banner'),('restore_fullbanner', 'Can restore page banner'))
    verbose_name = 'Content Banner'
    verbose_name_plural = 'Content Banners'

  def __str__(self):
    return self.title

  save = apps.common.functions.imagesave
  delete = apps.common.functions.modeltrash

# Create your models here.
