from .models import Language

def translationlinks(request):
  translation_items = Language.objects.filter(deleted=0).filter(published=1).order_by('tree_id','level','lft','rght','title')
  translation_items = list(translation_items.values())
  return {'TRANSLATION_ITEMS': translation_items}
