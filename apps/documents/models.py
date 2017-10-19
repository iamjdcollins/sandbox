from django.db import models
import apps.common.functions
from apps.objects.models import Node, Document as BaseDocument

class Document(BaseDocument):

  PARENT_URL = ''
  URL_PREFIX = '/documents/document/'

  title = models.CharField(max_length=200, help_text='')
  related_node = models.ForeignKey(Node, blank=True, null=True, related_name='documents_document_node', editable=False)

  document_document_node = models.OneToOneField(BaseDocument, db_column='document_document_node', on_delete=models.CASCADE, parent_link=True, editable=False)

  class Meta:
    db_table = 'documents_document'
    get_latest_by = 'update_date'
    permissions = (('trash_document', 'Can soft delete document'),('restore_document', 'Can restore document'))
    verbose_name = 'Document'
    verbose_name_plural = 'Documents'

  def __str__(self):
    return self.title

  save = apps.common.functions.documentsave
  delete = apps.common.functions.modeltrash