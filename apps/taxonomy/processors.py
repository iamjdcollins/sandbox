from .models import Language
from django.core.cache import cache

def translationlinks(request):
  translation_query = Language.objects.filter(deleted=0).filter(published=1).order_by('tree_id','level','lft','rght','title')
  translation_items = cache.get('TRANSLATION_ITEMS',None)
  if translation_items == None:
    translation_items = cache.get_or_set('TRANSLATION_ITEMS', list(translation_query.values()), 86400)
  return {'TRANSLATION_ITEMS': translation_items}
