from django.db import models
import apps.common.functions
from apps.objects.models import Node, Link

class ResourceLink(Link):

  PARENT_URL = '/links/resource-links/'
  URL_PREFIX = ''

  title = models.CharField(max_length=200, help_text='')
  link_url = models.CharField(max_length=2000, unique=True, db_index=True)
  related_nodes = models.ManyToManyField(Node, related_name='links_resourcelink_node')

  resourcelink_link_node = models.OneToOneField(Link, db_column='resourcelink_link_node', on_delete=models.CASCADE, parent_link=True, editable=False)

  class Meta:
    db_table = 'links_resourcelink'
    get_latest_by = 'update_date'
    permissions = (('trash_resourcelink', 'Can soft delete resource link'),('restore_resourcelink', 'Can restore resource link'))
    verbose_name = 'Resource Link'
    verbose_name_plural = 'Resource Links'

  def __str__(self):
    return self.title

  save = apps.common.functions.linksave
  delete = apps.common.functions.modeltrash