from django.shortcuts import render, get_object_or_404

# Create your views here.

from django.http import HttpResponse

from .models import Department, DepartmentSubPage

def departmentdetail(request):
  department = Department.objects.filter(url=request.path).first()
  departmentsubpage = DepartmentSubPage.objects.filter(url=request.path).first()
  if department:
    page = department
  elif departmentsubpage:
    page = departmentsubpage
  pageopts = page._meta 
  department_subpages = DepartmentSubPage.objects.filter(parent__department__url=request.path).filter(deleted=0).filter(published=1)
  department_children = Department.objects.filter(parent__url=request.path)
  return render(request, 'departments/departmentdetail.html', {'page': page,'pageopts': pageopts,  'department_subpages': department_subpages, 'department_children': department_children})
