from django.db import models
from apps.objects.models import DirectoryEntry
from apps.users.models import Employee
from apps.taxonomy.models import SchoolAdministratorType
import apps.common.functions

class SchoolAdministrator(DirectoryEntry):
  PARENT_URL = ''
  URL_PREFIX = '/directory/schooladministrator/'

  title = models.CharField(max_length=200, help_text='')
  employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='directoryenties_schooladministrator_employee')
  schooladministratortype = models.ForeignKey(SchoolAdministratorType, on_delete=models.CASCADE, related_name='directoryenties_schooladministrator_schooladministratortype')


  schooladministrator_directoryentry_node = models.OneToOneField(DirectoryEntry, db_column='schooladministrator_directoryentry_node', on_delete=models.CASCADE, parent_link=True,editable=False,)

  class Meta:
    db_table = 'directoryenties_schooladministrator'
    get_latest_by = 'create_date'
    verbose_name = 'School Administrator'
    verbose_name_plural = 'School Administrators'
 
  save = apps.common.functions.directoryentrysave
  delete = apps.common.functions.modeltrash
