from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.admin.utils import get_deleted_objects, model_ngettext
from django.core.exceptions import PermissionDenied
from django.db import router
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _, ugettext_lazy
from django.utils import timezone
from django.contrib.auth import get_permission_codename

def trash_selected(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    app_label = opts.app_label

    # Check that the user has delete permission for the actual model
    if not modeladmin.has_delete_permission(request):
        raise PermissionDenied

    using = router.db_for_write(modeladmin.model)

    # Populate deletable_objects, a data structure of all related objects that
    # will also be deleted.
    deletable_objects, model_count, perms_needed, protected = get_deleted_objects(
        queryset, opts, request.user, modeladmin.admin_site, using)

    #Redo Perms Needed To Support Django Guardian
    #perms_needed = set()
    #for obj in queryset:
    #  opts = obj._meta
    #  p = '%s.%s' % (opts.app_label,
    #                       get_permission_codename('delete', opts))
    #        if not user.has_perm(p):
    #            perms_needed.add(opts.verbose_name)
    
    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.
    if request.POST.get('post') and not protected:
        if perms_needed:
            raise PermissionDenied
        n = queryset.count()
        if n:
            for obj in queryset:
                if obj.deleted == 0:
                  obj.deleted = 1
                  obj.save()
                else:
                  obj.delete()
                obj_display = force_text(obj)
                modeladmin.log_deletion(request, obj, obj_display)
            modeladmin.message_user(request, _("Successfully deleted %(count)d %(items)s.") % {
                "count": n, "items": model_ngettext(modeladmin.opts, n)
            }, messages.SUCCESS)
        # Return None to display the change list page again.
        return None

    if len(queryset) == 1:
        objects_name = force_text(opts.verbose_name)
    else:
        objects_name = force_text(opts.verbose_name_plural)

    if perms_needed or protected:
        title = _("Cannot delete %(name)s") % {"name": objects_name}
    else:
        title = _("Are you sure?")

    context = dict(
        modeladmin.admin_site.each_context(request),
        title=title,
        objects_name=objects_name,
        deletable_objects=[deletable_objects],
        model_count=dict(model_count).items(),
        queryset=queryset,
        perms_lacking=perms_needed,
        protected=protected,
        opts=opts,
        action_checkbox_name=helpers.ACTION_CHECKBOX_NAME,
        media=modeladmin.media,
    )

    request.current_app = modeladmin.admin_site.name

    # Display the confirmation page
    return TemplateResponse(request, [
        "admin/%s/%s/trash_selected_confirmation.html" % (app_label, opts.model_name),
        "admin/%s/trash_selected_confirmation.html" % app_label,
        "admin/trash_selected_confirmation.html"
    ], context)

trash_selected.short_description = ugettext_lazy("Delete selected %(verbose_name_plural)s")

def restore_selected(modeladmin, request, queryset):
  opts = modeladmin.model._meta
  app_label = opts.app_label

  # Check that the user has delete permission for the actual model
  for obj in queryset:
    if not request.user.has_perm(app_label + '.restore_' + opts.model_name, obj=obj):
      raise PermissionDenied

  # Do the restore and return a None to display the change list view again.
  n = queryset.count()
  if n:
    for obj in queryset:
      if obj.deleted == 1:
        obj.deleted = 0
        obj.save()
    modeladmin.message_user(request, _("Successfully restore %(count)d %(items)s.") % {
      "count": n, "items": model_ngettext(modeladmin.opts, n)
    }, messages.SUCCESS)
    # Return None to display the change list page again.
    return None

  if len(queryset) == 1:
    objects_name = force_text(opts.verbose_name)
  else:
    objects_name = force_text(opts.verbose_name_plural)

  request.current_app = modeladmin.admin_site.name

restore_selected.short_description = ugettext_lazy("Restore selected %(verbose_name_plural)s")

def publish_selected(modeladmin, request, queryset):
  opts = modeladmin.model._meta
  app_label = opts.app_label

  # Check that the user has delete permission for the actual model
  for obj in queryset:
    if not request.user.has_perm(app_label + '.change_' + opts.model_name, obj=obj):
      raise PermissionDenied

  # Do the publish and return a None to display the change list view again.
  n = queryset.count()
  if n:
    queryset.update(published=1,update_date=timezone.now(),update_user=request.user)
    modeladmin.message_user(request, _("Successfully publish %(count)d %(items)s.") % {
      "count": n, "items": model_ngettext(modeladmin.opts, n)
    }, messages.SUCCESS)
    # Return None to display the change list page again.
    return None

  if len(queryset) == 1:
    objects_name = force_text(opts.verbose_name)
  else:
    objects_name = force_text(opts.verbose_name_plural)

  request.current_app = modeladmin.admin_site.name

publish_selected.short_description = ugettext_lazy("Publish selected %(verbose_name_plural)s")

def unpublish_selected(modeladmin, request, queryset):
  opts = modeladmin.model._meta
  app_label = opts.app_label

  # Check that the user has delete permission for the actual model
  for obj in queryset:
    if not request.user.has_perm(app_label + '.change_' + opts.model_name, obj=obj):
      raise PermissionDenied

  # Do the unpublish and return a None to display the change list view again.
  n = queryset.count()
  if n:
    queryset.update(published=0,update_date=timezone.now(),update_user=request.user)
    modeladmin.message_user(request, _("Successfully unpublish %(count)d %(items)s.") % {
      "count": n, "items": model_ngettext(modeladmin.opts, n)
    }, messages.SUCCESS)
    # Return None to display the change list page again.
    return None

  if len(queryset) == 1:
    objects_name = force_text(opts.verbose_name)
  else:
    objects_name = force_text(opts.verbose_name_plural)

  request.current_app = modeladmin.admin_site.name

unpublish_selected.short_description = ugettext_lazy("Unpublish selected %(verbose_name_plural)s")
