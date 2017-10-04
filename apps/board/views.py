from django.shortcuts import render, get_object_or_404

# Create your views here.

from django.http import HttpResponse
from datetime import datetime
from .models import Board, BoardSubPage, BoardPolicy, BoardMeeting

def board(request):
  board = Board.objects.filter(url=request.path).first() 
  boardsubpage = BoardSubPage.objects.filter(url=request.path).first()
  if board:
    page = board
  elif boardsubpage:
    page = boardsubpage
  pageopts = page._meta
  board_subpages = BoardSubPage.objects.filter(parent__board__url=request.path).filter(deleted=0).filter(published=1).order_by('tree_id','level','lft','rght')
  board_policies = BoardPolicy.objects.filter(deleted=0).filter(published=1).filter(section__title='Board Policies')
  community_policies = BoardPolicy.objects.filter(deleted=0).filter(published=1).filter(section__title='Community Policies')
  financial_policies = BoardPolicy.objects.filter(deleted=0).filter(published=1).filter(section__title='Financial Policies')
  general_policies = BoardPolicy.objects.filter(deleted=0).filter(published=1).filter(section__title='General Policies')
  instructional_policies = BoardPolicy.objects.filter(deleted=0).filter(published=1).filter(section__title='Instructional Policies')
  personnel_policies = BoardPolicy.objects.filter(deleted=0).filter(published=1).filter(section__title='Personnel Policies')
  student_policies = BoardPolicy.objects.filter(deleted=0).filter(published=1).filter(section__title='Student Policies')
  board_meetings = BoardMeeting.objects.filter(deleted=0).filter(published=1)
  board_meeting_years = {}
  board_meeting_years['years'] = {}
  for meeting in board_meetings:
    if meeting.startdate.month >= 7:
      year = meeting.startdate.year + 1
      year_string =  'School Year: ' + str(meeting.startdate.year) + '-' + str(meeting.startdate.year + 1)[2:]
    else:
      year = meeting.startdate.year
      year_string =  'School Year: ' + str(meeting.startdate.year - 1) + '-' + str(meeting.startdate.year)[2:]
    board_meeting_years['years'][year] = year_string
  currentdate = datetime.now()
  if currentdate.month >= 7:
    board_meeting_years['current'] = currentdate.year + 1
  else:
    board_meeting_years['current'] = currentdate.year
  return render(request, 'board/boarddetail.html', {'page': page,'pageopts': pageopts, 'board_subpages': board_subpages, 'board_policies': board_policies, 'community_policies': community_policies, 'financial_policies': financial_policies, 'general_policies': general_policies, 'instructional_policies': instructional_policies, 'personnel_policies': personnel_policies, 'student_policies': student_policies, 'board_meeting_years': board_meeting_years, 'board_meetings': board_meetings})
