from django.db import models
import apps.common.functions
from apps.objects.models import Node, Link

class ResourceLink(Link):

  PARENT_URL = '/links/resource-links/'
  URL_PREFIX = ''

  title = models.CharField(max_length=200, help_text='')
  link = models.ImageField(max_length=2000, upload_to=apps.common.functions.image_upload_to, verbose_name='Image', help_text='')
  node = models.ManyToManyField(Node, related_name='links_resourcelink_node')

  resourcelink_link_node = models.OneToOneField(Image, db_column='resourcelink_link_node', on_delete=models.CASCADE, parent_link=True, editable=False)

  class Meta:
    db_table = 'links_resourcelink'
    get_latest_by = 'update_date'
    permissions = (('trash_resourcelink', 'Can soft delete resource link'),('restore_thumbnail', 'Can restore resource link'))
    verbose_name = 'Resource Link'
    verbose_name_plural = 'Resource Links'

  def __str__(self):
    return self.title

  save = apps.common.functions.linksave
  delete = apps.common.functions.modeltrash