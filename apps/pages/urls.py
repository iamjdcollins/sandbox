from django.conf.urls import url

from . import views
from .models import Page

Pages = Page.objects.filter(deleted=0).filter(published=1)

urlpatterns = [
  url(r'^$', views.home, name='home'),
  url(r'^home/$', views.home, name='home'),
  # url(r'^news/$', views.news, name='news'),
  url(r'^schools/$', views.schools, name='schools'),
  url(r'^schools/elementary-schools/$', views.elementaryschools, name='elementaryschools'),
  url(r'^schools/k-8-schools/$', views.k8schools, name='k8schools'),
  url(r'^schools/middle-schools/$', views.middleschools, name='middleschools'),
  url(r'^schools/high-schools/$', views.highschools, name='highschools'),
  url(r'^schools/charter-schools/$', views.charterschools, name='charterschools'),
  url(r'^schools/[a-z0-9-]+\/[a-z0-9-]+\/$', views.schooldetail, name='schooldetail'),
  # url(r'^departments/$', views.departments, name='departments'),
  # url(r'^directory/$', views.directory, name='directory'),
  # url(r'^directory/last-name-(?P<letter>[a-z])/$', views.directory_letter, name='directory_letter'),
  # url(r'^calendars/$', views.calendars, name='calendars'),
  # url(r'^temp/$', views.temp, name='temp'),
]

