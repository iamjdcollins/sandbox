from apps.sitestructure.models import SiteStructure
import mptt

def breadcrumb(request):
  breadcrumb = SiteStructure.objects.filter(url=request.path).get_ancestors(include_self=True)
  return {'BREADCRUMB': breadcrumb}

def mainmenu(request):
  menu_items = SiteStructure.objects.filter(menu_item=1).filter(level=0)
  return {'MENU_ITEMS': menu_items}

def sitestructure(requset):
  sitestructure = SiteStructure.objects.all()
  return {'SITESTRUCTURE': sitestructure}
