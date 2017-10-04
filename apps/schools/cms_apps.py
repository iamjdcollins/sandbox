from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _

class SchoolsApp(CMSApp):
  name = _('Schools')
  urls = ['apps.schools.urls', ]
  app_name = 'schools'

apphook_pool.register(SchoolsApp)
