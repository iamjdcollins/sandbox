from ajax_select import register
from apps.common.classes import UUIDLookupChannel
from apps.users.models import Employee

@register('employee')
class EmployeesLookup(UUIDLookupChannel):
  model = Employee

  def get_query(self, q, request):
    return self.model.objects.filter(username__icontains=q)[:10]

  def format_item_display(self, item):
    return u"<span class='employee'>%s</span>" % item.username
