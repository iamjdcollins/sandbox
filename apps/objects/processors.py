from .models import Node
import mptt

def breadcrumb(request):
  breadcrumb = Node.objects.filter(url=request.path).get_ancestors(include_self=True)
  return {'BREADCRUMB': breadcrumb}

def mainmenu(request):
  menu_items = Node.objects.filter(menu_item=1).filter(level=0)
  return {'MENU_ITEMS': menu_items}

def sitestructure(requset):
  sitestructure = Node.objects.all()
  return {'SITESTRUCTURE': sitestructure}
