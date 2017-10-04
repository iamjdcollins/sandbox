from django.shortcuts import render, get_object_or_404

# Create your views here.

from django.http import HttpResponse

from .models import School

def schooldetail(request):
  page = get_object_or_404(School, url=request.path)
  pageopts = page._meta
  return render(request, 'schools/schooldetail.html', {'page': page,'pageopts': pageopts,})
