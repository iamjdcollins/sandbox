from django.apps import AppConfig
from mptt.signals import node_moved

from .signals import save_node

class DepartmentsConfig(AppConfig):
    name = 'apps.departments'

    def ready(self):
      node_moved.connect(save_node)
