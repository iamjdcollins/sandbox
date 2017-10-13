from django.db import models
from apps.objects.models import DirectoryEntry
from apps.users.models import Employee
import apps.common.functions

class SchoolAdministrator(DirectoryEntry):
  PARENT_URL = ''
  URL_PREFIX = '/directory/schooladministrator/'

  title = models.CharField(max_length=200, help_text='')
  employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='directoryenties_schooladministrator_employee')


  schooladministrator_directoryentry_node = models.OneToOneField(DirectoryEntry, db_column='schooladministrator_directoryentry_node', on_delete=models.CASCADE, parent_link=True,editable=False,)

  class Meta:
    db_table = 'directoryenties_schooladministrator'
    get_latest_by = 'create_date'
    verbose_name = 'School Administrator'
    verbose_name_plural = 'School Administrators'
 
  save = apps.common.functions.directoryentrysave
  delete = apps.common.functions.modeltrash
