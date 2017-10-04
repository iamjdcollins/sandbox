from django.conf.urls import url

from . import views

urlpatterns = [
  url(r'^(?:[a-z0-9-]+\/)*$', views.board, name='boardsubpage'),
]
