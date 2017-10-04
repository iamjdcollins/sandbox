"""www_slcschools_org URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.views.static import serve
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from ajax_select import urls as ajax_select_urls
import django_saml2_auth.views
from django.contrib.auth.views import logout

urlpatterns = [
url(r'^saml_login/', include('django_saml2_auth.urls')),
url(r'^accounts/login/$', django_saml2_auth.views.signin),
url(r'^accounts/logout/$', logout,{'next_page': 'https://adfs.slcschools.org/adfs/ls/?wa=wsignout1.0&wreply=https://www2.slcschools.org/'})
#url(r'^admin/login/$', django_saml2_auth.views.signin),
]

#Pages App
urlpatterns +=[
  url(r'', include('apps.pages.urls', namespace='pages')),
]

#Board App
#urlpatterns += [
#    url(r'^board-of-education/', include('apps.board.urls', namespace='board')),
#]


#Schools App
#urlpatterns += [
#   url(r'^schools/', include('apps.schools.urls', namespace='schools')),
#]

#Departments App
#urlpatterns += [
#    url(r'^departments/', include('apps.departments.urls', namespace='departments')),
#]
admin.site.site_header = 'Salt Lake City School District'
admin.site.index_title = ('Salt Lake City School District')
admin.site.site_title = ('Salt Lake City School District')
urlpatterns += [
    # url(r'^jet/', include('jet.urls', 'jet')),
    # url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    url(r'^ajax_select/', include(ajax_select_urls)),
    url(r'^admin/', admin.site.urls),
]

#News App
#urlpatterns += [
#  url(r'^news/', include('apps.news.urls', namespace='news')),
#]

# This is only needed when using runserver.
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        #url(r'^__debug__/', include(debug_toolbar.urls)),
        url(r'^(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        ] + staticfiles_urlpatterns() #+ urlpatterns
