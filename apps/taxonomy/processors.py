from .models import Language
from django.core.cache import cache

def translationlinks(request):
  translation_items = Language.objects.filter(deleted=0).filter(published=1).order_by('tree_id','level','lft','rght','title')
  translation_items = cache.get_or_set('TRANSLATION_ITEMS', list(translation_items.values()), 86400)
  return {'TRANSLATION_ITEMS': translation_items}
