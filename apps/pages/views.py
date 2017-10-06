from django.shortcuts import render, get_object_or_404

# Create your views here.

from django.http import HttpResponse

from .models import Page, School
# from apps.schools.models import School
# from apps.departments.models import Department
# from apps.news.models import News, NewsYear
#from apps.users.models import User

def home(request):
  page = get_object_or_404(Page, url='/home/')
  pageopts = page._meta
  # news = News.objects.all().filter(deleted=0).filter(published=1).order_by('-pinned','-author_date')[0:5]
  return render(request, 'pages/home.html', {'page': page,'pageopts': pageopts,})# 'news': news})

# def news(request):
#   page = get_object_or_404(Page, url=request.path)
#   pageopts = page._meta
#   newsyears = NewsYear.objects.all().order_by('-yearend')
#   return render(request, 'pages/news/newsyears.html', {'page': page,'pageopts': pageopts,'newsyears': newsyears})

def schools(request):
  page = get_object_or_404(Page, url=request.path)
  pageopts = page._meta
  elementary_schools = School.objects.filter(deleted=0).filter(published=1).filter(schooltype__title='Elementary Schools').order_by('title')
  k8_schools = School.objects.filter(deleted=0).filter(published=1).filter(schooltype__title='K-8 Schools').order_by('title')
  middle_schools = School.objects.filter(deleted=0).filter(published=1).filter(schooltype__title='Middle Schools').order_by('title')
  high_schools = School.objects.filter(deleted=0).filter(published=1).filter(schooltype__title='High Schools').order_by('title')
  charter_schools = School.objects.filter(deleted=0).filter(published=1).filter(schooltype__title='Charter Schools').order_by('title')
  return render(request, 'pages/schools/main_school_directory.html', {'page': page,'pageopts': pageopts, 'elementary_schools': elementary_schools, 'k8_schools': k8_schools,'middle_schools': middle_schools,'high_schools': high_schools,'charter_schools': charter_schools})

# def temp(request):
#   schools = School.objects.filter(deleted=0).filter(published=1).order_by('title')
#   return render(request, 'pages/schools/temp.html', {'schools': schools,})

# def elementaryschools(request):
#   page = get_object_or_404(Page, url=request.path)
#   pageopts = page._meta
#   schools = School.objects.filter(deleted=0).filter(published=1).filter(parent__url='/schools/elementary-schools/').order_by('title') 
#   return render(request, 'pages/schools/school_directory.html', {'page': page,'pageopts': pageopts, 'schools': schools})

# def k8schools(request):
#   page = get_object_or_404(Page, url=request.path)
#   pageopts = page._meta
#   schools = School.objects.filter(deleted=0).filter(published=1).filter(parent__url='/schools/k-8-schools/').order_by('title')
#   return render(request, 'pages/schools/school_directory.html', {'page': page,'pageopts': pageopts, 'schools': schools})

# def middleschools(request):
#   page = get_object_or_404(Page, url=request.path)
#   pageopts = page._meta
#   schools = School.objects.filter(deleted=0).filter(published=1).filter(parent__url='/schools/middle-schools/').order_by('title')
#   return render(request, 'pages/schools/school_directory.html', {'page': page,'pageopts': pageopts, 'schools': schools})

# def highschools(request):
#   page = get_object_or_404(Page, url=request.path)
#   pageopts = page._meta
#   schools = School.objects.filter(deleted=0).filter(published=1).filter(parent__url='/schools/high-schools/').order_by('title')
#   return render(request, 'pages/schools/school_directory.html', {'page': page,'pageopts': pageopts, 'schools': schools})

# def charterschools(request):
#   page = get_object_or_404(Page, url=request.path)
#   pageopts = page._meta
#   schools = School.objects.filter(deleted=0).filter(published=1).filter(parent__url='/schools/charter-schools/').order_by('title')
#   return render(request, 'pages/schools/school_directory.html', {'page': page,'pageopts': pageopts, 'schools': schools})

# def departments(request):
#   page = get_object_or_404(Page, url=request.path)
#   pageopts = page._meta
#   departments = Department.objects.filter(deleted=0).filter(published=1).order_by('title')
#   return render(request, 'pages/departments/department_directory.html', {'page': page,'pageopts': pageopts, 'departments': departments})

# def directory(request):
#   page = get_object_or_404(Page, url=request.path)
#   pageopts = page._meta
#   people = User.objects.filter(is_active=1).filter(is_staff=1).order_by('last_name')
#   return render(request, 'pages/directory/directory.html', {'page': page,'pageopts': pageopts, 'people': people})

# def directory_letter(request, letter):
#   page = get_object_or_404(Page, url=request.path)
#   pageopts = page._meta
#   people = User.objects.filter(is_active=1).filter(is_staff=1).filter(last_name__istartswith=letter).order_by('last_name')
#   return render(request, 'pages/directory/directory_letter.html', {'page': page,'pageopts': pageopts, 'people': people})

# def calendars(request):
#   page = get_object_or_404(Page, url=request.path)
#   pageopts = page._meta
#   return render(request, 'pages/pagedetail.html', {'page': page,'pageopts': pageopts})
