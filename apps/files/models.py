from django.db import models
import apps.common.functions
from apps.objects.models import Node, File as BaseFile
from apps.taxonomy.models import Language

class File(BaseFile):

  PARENT_URL = ''
  URL_PREFIX = ''

  title = models.CharField(max_length=200, help_text='')
  file_file = models.FileField(max_length=2000, upload_to=apps.common.functions.file_upload_to, verbose_name='File', help_text='')
  file_language = models.ForeignKey(Language, to_field='language_taxonomy_node', on_delete=models.PROTECT, limit_choices_to={'deleted': False,}, help_text='', related_name='files_file_file_language')
  related_node = models.ForeignKey(Node, blank=True, null=True, related_name='files_file_node', editable=False)
  

  file_file_node = models.OneToOneField(BaseFile, db_column='file_file_node', on_delete=models.CASCADE, parent_link=True, editable=False)

  class Meta:
    db_table = 'files_file'
    get_latest_by = 'update_date'
    permissions = (('trash_file', 'Can soft delete file'),('restore_file', 'Can restore file'))
    verbose_name = 'File'
    verbose_name_plural = 'Files'

  # def __str__(self):
  #   return self.title

  save = apps.common.functions.filesave
  delete = apps.common.functions.modeltrash