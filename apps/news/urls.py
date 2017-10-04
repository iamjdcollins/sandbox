from django.conf.urls import url

from . import views

urlpatterns = [
  #url(r'^(?:[a-z0-9-]+\/)*$', views.YearArchive, name='yeararchive'),
  url(r'^\d\d\d\d-\d\d\/$', views.YearArchive, name='yeararchive'),
  url(r'^.*\/$', views.ArticleDetail, name='articledetail'),
]
