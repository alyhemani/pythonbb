from django.shortcuts import render, redirect
from models import *
from django.contrib import messages
import bcrypt
import re 
import datetime
EMAIL_REGEX= re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
DATE_REGEX =  re.compile(r'^(19|20)\d\d[\-\/.](0[1-9]|1[012])[\-\/.](0[1-9]|[12][0-9]|3[01])$')

# Create your views here.
def index(request):
	return render(request, 'first/index.html')

def register(request):
	if len(request.POST.get('name'))<2:
		messages.warning(request, 'Please enter valid name')
		return redirect('/')
	elif len(request.POST.get('email'))<1:
		messages.warning(request, 'Please enter valid email')
		return redirect('/')
	elif len(request.POST.get('password'))<1:
		messages.warning(request, 'Please enter valid password')
		return redirect('/')
	elif len(request.POST.get('confirm'))<1:
		messages.warning(request, 'Please enter valid password confirmation')
		return redirect('/')
	elif request.POST.get('password') != request.POST.get('confirm'):
		messages.warning(request, 'Password and Confirmation should match')
		return redirect('/')
	elif not EMAIL_REGEX.match(request.POST.get('email')):
		messages.warning(request, 'Please enter the Email in valid form')
		return redirect('/')
	elif not DATE_REGEX.match(request.POST.get('birth')):
		messages.warning(request, 'Please enter valid Date of Birth')
		return redirect('/')
	else:
		user = User.objects.create(
			name=request.POST.get('name'),
			email=request.POST.get('email'),
			password=bcrypt.hashpw(request.POST.get('password').encode(), bcrypt.gensalt()),
			dob=request.POST.get('birth')
			)
		request.session['user_id']= user.id
		return redirect('/appointments')

def login(request):
	login = User.objects.login(request.POST)
	if login[0]:
		request.session['user_id'] = login[1].id
		return redirect('/appointments')
	else:
		messages.warning(request, 'No matching user. Please Register or Enter Proper Information')	
		return redirect('/')



def appointments(request):
	today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
	today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
	context = {
	'tasks': Task.objects.filter(user__id=request.session['user_id']).order_by('date', 'time').exclude(date__range=(today_min, today_max), user__id=request.session['user_id']),
	'today': Task.objects.filter(date__range=(today_min, today_max), user__id=request.session['user_id']).order_by('time'),
	}
	return render(request, 'first/appointments.html', context)

def add(request):
	if not DATE_REGEX.match(request.POST.get('date')):
		messages.warning(request, 'Please enter valid date')
	elif len(request.POST.get('task'))<1:
		messages.warning(request, 'Please enter valid task')
	elif request.POST.get('time') == '':
		messages.warning(request, 'Please enter valid time')
	else:
		Task.objects.create(
			task=request.POST.get('task'),
			date = request.POST.get('date'),
			time = request.POST.get('time'),
			user = User.objects.get(id=request.session['user_id']),
			status = 'Pending'
			)
		print "created Task"
	return redirect('/appointments')

def edit(request, id):
	context = {
	'task': Task.objects.get(id=id)
	}
	return render(request, 'first/edit.html', context)

def delete(request, id):
	Task.objects.filter(id=id).delete()
	return redirect('/appointments')

def update(request, id):
	if not DATE_REGEX.match(request.POST.get('date')):
		messages.warning(request, 'Please enter valid date')
	elif len(request.POST.get('task'))<1:
		messages.warning(request, 'Please enter valid task')
	elif request.POST.get('time') == '':
		messages.warning(request, 'Please enter valid time')
	else:
		Task.objects.filter(id=id).delete()
		Task.objects.create(
			task=request.POST.get('task'),
			date=request.POST.get('date'),
			time=request.POST.get('time'),
			user= User.objects.get(id=request.session['user_id']),
			status = request.POST.get('status')
			)
		return redirect('/appointments')
	return redirect('/appointments/{}'.format(id))




