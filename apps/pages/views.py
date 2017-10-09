from django.shortcuts import render, get_object_or_404
from django.core.cache import cache

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
  elementary_schools = []
  k8_schools = []
  middle_schools = []
  high_schools = []
  charter_schools = []
  
  def school_dict(school):
    return [{
      'schooltype': school.schooltype.title,
      'thumbnails': school.thumbnails(),
      'title': school.title,
      'building_location': {
        'street_address': school.building_location.street_address,
        'city': school.building_location.location_city.title,
        'state': school.building_location.location_state.title,
        'zipcode': school.building_location.location_zipcode.title,
      },
      'main_phone': school.main_phone,
      'website_url': school.website_url,
      'url': school.url,
    }]

  page = get_object_or_404(Page, url=request.path)
  pageopts = page._meta
  schools_query = School.objects.filter(deleted=0).filter(published=1).order_by('title').select_related()
  schools_directory = cache.get('SCHOOLS_DIRECTORY',None)
  if schools_directory == None:
    schools_directory = []
    for school in schools_query:
      schools_directory += school_dict(school)
    schools_directory = cache.get_or_set('SCHOOLS_DIRECTORY', schools_directory, 86400)
  elementary_schools_directory = cache.get('ELEMENTARY_SCHOOLS_DIRECTORY',None)
  if elementary_schools_directory == None:
    elementary_schools_directory = []
    for school in schools_directory:
      if school['schooltype'] == 'Elementary Schools':
        elementary_schools_directory += [school]
    elementary_schools_directory = cache.get_or_set('ELEMENTARY_SCHOOLS_DIRECTORY', elementary_schools_directory, 86400)
  k8_schools_directory = cache.get('K8_SCHOOLS_DIRECTORY',None)
  if k8_schools_directory == None:
    k8_schools_directory = []
    for school in schools_directory:
      if school['schooltype'] == 'K-8 Schools':
        k8_schools_directory += [school]
    k8_schools_directory = cache.get_or_set('K8_SCHOOLS_DIRECTORY', k8_schools_directory, 86400)
  middle_schools_directory = cache.get('MIDDLE_SCHOOLS_DIRECTORY',None)
  if middle_schools_directory == None:
    middle_schools_directory = []
    for school in schools_directory:
      if school['schooltype'] == 'Middle Schools':
        middle_schools_directory += [school]
    middle_schools_directory = cache.get_or_set('MIDDLE_SCHOOLS_DIRECTORY', middle_schools_directory, 86400)
  high_schools_directory = cache.get('HIGH_SCHOOLS_DIRECTORY',None)
  if high_schools_directory == None:
    high_schools_directory = []
    for school in schools_directory:
      if school['schooltype'] == 'High Schools':
        high_schools_directory += [school]
    high_schools_directory = cache.get_or_set('HIGH_SCHOOLS_DIRECTORY', high_schools_directory, 86400)
  charter_schools_directory = cache.get('CHARTER_SCHOOLS_DIRECTORY',None)
  if charter_schools_directory == None:
    charter_schools_directory = []
    for school in schools_directory:
      if school['schooltype'] == 'Charter Schools':
        charter_schools_directory += [school]
    k8_schools_directory = cache.get_or_set('CHARTER_SCHOOLS_DIRECTORY', charter_schools_directory, 86400)
  # k8_schools = School.objects.filter(deleted=0).filter(published=1).filter(schooltype__title='K-8 Schools').order_by('title')
  # middle_schools = School.objects.filter(deleted=0).filter(published=1).filter(schooltype__title='Middle Schools').order_by('title')
  # high_schools = School.objects.filter(deleted=0).filter(published=1).filter(schooltype__title='High Schools').order_by('title')
  # charter_schools = School.objects.filter(deleted=0).filter(published=1).filter(schooltype__title='Charter Schools').order_by('title')
  return render(request, 'pages/schools/main_school_directory.html', {'page': page,'pageopts': pageopts, 'elementary_schools_directory': elementary_schools_directory, 'k8_schools_directory': k8_schools_directory,'middle_schools_directory': middle_schools_directory,'high_schools_directory': high_schools_directory,'charter_schools_directory': charter_schools_directory})

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
