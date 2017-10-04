from apps.translationlinks.models import TranslationLink

def translationlinks(request):
  translation_items = TranslationLink.objects.filter(deleted=0).filter(published=1).order_by('tree_id','level','lft','rght','title')
  translation_items = list(translation_items.values())
  return {'TRANSLATION_ITEMS': translation_items}
