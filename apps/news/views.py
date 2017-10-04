from django.shortcuts import render, get_object_or_404

# Create your views here.

from django.http import HttpResponse
from datetime import datetime
from .models import News, NewsYear

def YearArchive(request):
  page = NewsYear.objects.filter(url=request.path).first()
  pageopts = page._meta
  news = News.objects.filter(parent__url=request.path).filter(deleted=0).filter(published=1)
  newsmonths = [ 
    {'month': 'June', 'news': News.objects.filter(author_date__month=6).filter(parent__url=request.path).filter(deleted=0).filter(published=1)},
    {'month': 'May', 'news': News.objects.filter(author_date__month=5).filter(parent__url=request.path).filter(deleted=0).filter(published=1),},
    {'month': 'April', 'news': News.objects.filter(author_date__month=4).filter(parent__url=request.path).filter(deleted=0).filter(published=1),},
    {'month': 'March', 'news': News.objects.filter(author_date__month=3).filter(parent__url=request.path).filter(deleted=0).filter(published=1),},
    {'month': 'February', 'news': News.objects.filter(author_date__month=2).filter(parent__url=request.path).filter(deleted=0).filter(published=1),},
    {'month': 'January', 'news': News.objects.filter(author_date__month=1).filter(parent__url=request.path).filter(deleted=0).filter(published=1),},
    {'month': 'December', 'news': News.objects.filter(author_date__month=12).filter(parent__url=request.path).filter(deleted=0).filter(published=1),},
    {'month': 'November', 'news': News.objects.filter(author_date__month=11).filter(parent__url=request.path).filter(deleted=0).filter(published=1),},
    {'month': 'October', 'news': News.objects.filter(author_date__month=10).filter(parent__url=request.path).filter(deleted=0).filter(published=1),},
    {'month': 'September', 'news': News.objects.filter(author_date__month=9).filter(parent__url=request.path).filter(deleted=0).filter(published=1),},
    {'month': 'August', 'news': News.objects.filter(author_date__month=8).filter(parent__url=request.path).filter(deleted=0).filter(published=1),},
    {'month': 'July', 'news': News.objects.filter(author_date__month=7).filter(parent__url=request.path).filter(deleted=0).filter(published=1),},
  ]
  return render(request, 'news/yeararchive.html', {'page': page, 'pageopts': pageopts, 'news': news, 'newsmonths': newsmonths})

def ArticleDetail(request):
  pages =  News.objects.filter(published=1).filter(deleted=0)
  page = get_object_or_404(pages, url=request.path)
  pageopts = page._meta
  return render(request, 'news/articledetail.html', {'page': page, 'pageopts': pageopts})
