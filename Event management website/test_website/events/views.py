from django.shortcuts import render, redirect
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from .models import Event, Venue
#import User model from django
from django.contrib.auth.models import User
from .forms import VenueForm,EventForm,EventFormAdmin
from django.http import HttpResponseRedirect
from django.http import HttpResponse,FileResponse
import csv 

from django.contrib import messages

from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from django.core.paginator import Paginator

def show_event(request,event_id):
	event= Event.objects.get(pk=event_id)
	return render(request,'events/show_event.html',{
		"event":event,
		})

#Show events in a venue
def venue_events(request,venue_id):
	#grab the venue
	venue=Venue.objects.get(id=venue_id)
	#grab events from that venue
	events=venue.event_set.all()
	if events:
		return render(request,'events/venue_events.html',{
			"events":events,
			})
	else:
		messages.success(request,("That venue has no events at that time"))
		return redirect('admin-approval')

#create admin approval page
def admin_approval(request):
	#get the venues
	venue_list=Venue.objects.all()
	#get counts
	event_count=Event.objects.all().count()
	venue_count=Venue.objects.all().count()
	user_count=User.objects.all().count()

	event_list=Event.objects.all().order_by('-event_date')
	if request.user.is_superuser:
		if request.method=="POST":
			id_list= request.POST.getlist('boxes')

			#uncheck all events
			event_list.update(approved=False)

			#update datebase
			for x in id_list:
				Event.objects.filter(pk=int(x)).update(approved=True)

			messages.success(request,("Success"))
			return redirect('list-events')

		else:
			return render(request,'events/admin_approval.html',{
				'event_list':event_list,
				"event_count":event_count,
				"venue_count":venue_count,
				"user_count":user_count,
				"venue_list":venue_list,
				})
	else:
		messages.success(request,("You aren't authorized to view this page"))
		return redirect('home')



def search_events(request):
	if request.method=="POST":
		searched=request.POST['searched']
		events=Event.objects.filter(description__contains=searched)
		return render(request,'events/search_events.html',
		{"searched":searched,
		'events':events})
	else:
		return render(request,'events/search_events.html',{	})

#create my events page
def my_events(request):
	if request.user.is_authenticated:
		me=request.user.id
		events=Event.objects.filter(attendees=me)
		return render(request,
			'events/my_events.html',
			{
			"events":events
			})
	else:
		messages.success(request,("You aren't authorized to view this pagee"))
		return redirect('home')

#generate pdf file venue list
def venue_pdf(request):
	#create a bytestream buffer
	buf = io.BytesIO()
	#create canvas
	c=canvas.Canvas(buf,pagesize=letter,bottomup=0)
	#create a text obj
	textob=c.beginText()
	textob.setTextOrigin(inch,inch)
	textob.setFont("Helvetica",14)
	#Add text
	# lines=["This is line 1\n","This is line 2\n","This is line 3\n"]
	
	#designate the model
	venues=Venue.objects.all()

	lines=[]
	for venue in venues:
		lines.append(venue.name)
		lines.append(venue.address)
		lines.append(venue.zip_code)
		lines.append(venue.phone)
		lines.append(venue.web)
		lines.append(venue.email_address)
		lines.append(" ")

	for line in lines:
		textob.textLine(line)

	c.drawText(textob)
	c.showPage()
	c.save()
	buf.seek(0)

	return FileResponse(buf,as_attachment=True,filename='venue.pdf')
#generate csv file venue list
def venue_csv(request):
	response=HttpResponse(content_type='text/csv')
	response['Content-Disposition']='attachment; filename=venues.csv'

	#create csv writer
	writer=csv.writer(response)
	#designate the model
	venues=Venue.objects.all()

	#add column headings
	writer.writerow(['Venue Name','Address','Zip Code','Phone','Web','Email'])

	for venue in venues:
		writer.writerow([venue.name,venue.address,venue.zip_code,venue.phone,venue.web,venue.email_address])

	return response


#generate text file venue list
def venue_text(request):
	response=HttpResponse(content_type='text/plain')
	response['Content-Disposition']='attachment; filename=venues.txt'

	# lines=["This is line 1\n","This is line 2\n","This is line 3\n"]
	# #write to text file
	# response.writelines(lines)

	#designate the model
	venues=Venue.objects.all()
	lines=[]
	for venue in venues:
		lines.append(f'{venue.name}\n{venue.address}\n{venue.zip_code}\n{venue.phone}\n{venue.web}\n{venue.email_address}\n\n\n')
	response.writelines(lines)
	return response

#delete an event
def delete_event(request,event_id):
	event= Event.objects.get(pk=event_id)
	if request.user==event.manager:
		event.delete()
		messages.success(request,('Event deleted.'))
		return redirect('list-events')
	else:
		messages.success(request,("You aren't authorized to delete this event"))
		return redirect('list-events')

#delete an venue
def delete_venue(request,venue_id):
	venue= Venue.objects.get(pk=venue_id)
	venue.delete()
	return redirect('list-venues')

def update_event(request,event_id):
	event= Event.objects.get(pk=event_id)
	if request.user.is_superuser:
		form=EventFormAdmin(request.POST or None, instance=event)
	else:
		form=EventForm(request.POST or None, instance=event)
	if form.is_valid():
		form.save()
		return redirect('list-events')
	return render(request,'events/update_event.html',{
		"event":event,
		"form":form
		})

def add_event(request):
	submitted=False
	if request.method=="POST":
		if request.user.is_superuser:
			form=EventFormAdmin(request.POST)

			if form.is_valid():
				form.save()
				return HttpResponseRedirect('/add_event?submitted=True')
		else:
			form=EventForm(request.POST)

			if form.is_valid():
				# form.save()
				event=form.save(commit=False)
				event.manager=request.user #logged in user
				event.save()
				return HttpResponseRedirect('/add_event?submitted=True')
	else:
		#just going to the page not submitting
		if request.user.is_superuser:
			form=EventFormAdmin
		else:
			form=EventForm
		if 'submitted' in request.GET:
			submitted=True
	return render(request,'events/add_event.html',{
		"form":form,
		"submitted":submitted
		})

def update_venue(request,venue_id):
	venue= Venue.objects.get(pk=venue_id)
	form=VenueForm(request.POST or None,request.FILES or None, instance=venue)
	if form.is_valid():
		form.save()
		return redirect('list-venues')
	return render(request,'events/update_venue.html',{
		"venue":venue,
		"form":form
		})

def search_venues(request):
	if request.method=="POST":
		searched=request.POST['searched']
		venues=Venue.objects.filter(name__contains=searched)
		return render(request,'events/search_venues.html',
		{"searched":searched,
		'venues':venues})
	else:
		return render(request,'events/search_venues.html',{	})

def show_venue(request,venue_id):
	venue= Venue.objects.get(pk=venue_id)
	#grab events from that venue
	events=venue.event_set.all()

	venue_owner=User.objects.get(pk=venue.owner)
	return render(request,'events/show_venue.html',{
		"venue":venue,
		"venue_owner":venue_owner,
		"events":events,
		})

def list_venues(request):
	# venue_list=Venue.objects.all().order_by('?') #randon ordering 
	# venue_list=Venue.objects.all().order_by('name')
	# venue_list=Venue.objects.all()

	#set up pagination
	p=Paginator(Venue.objects.all(),3)
	page =request.GET.get('page')
	venues=p.get_page(page)
	nums= "a" * venues.paginator.num_pages

	return render(request,'events/venues.html',{
		# "venue_list":venue_list,
		"venues":venues,
		"nums": nums
		})

def add_venue(request):
	submitted=False
	if request.method=="POST":
		form=VenueForm(request.POST,request.FILES)
		if form.is_valid():
			# form.save()
			venue=form.save(commit=False)
			venue.owner=request.user.id #logged in user
			venue.save()
			return HttpResponseRedirect('/add_venue?submitted=True')
	else:
		form=VenueForm
		if 'submitted' in request.GET:
			submitted=True
	return render(request,'events/add_venue.html',{
		"form":form,
		"submitted":submitted
		})

def all_events(request):
	event_list=Event.objects.all().order_by('-event_date')
	return render(request,'events/event_list.html',{
		"event_list":event_list
		})

def home(request,year=datetime.now().year,month=datetime.now().strftime('%B')):
	name="Sai"
	month=month.capitalize()
	#convert moth from name to number
	month_number=list(calendar.month_name).index(month)
	month_number=int(month_number)
	
	#create calendar

	cal=HTMLCalendar().formatmonth(
		year,
		month_number)

	now=datetime.now()
	current_year= now.year
	
	#query events model for date
	event_list=Event.objects.filter(
		event_date__year=year,
		event_date__month=month_number
		)

	time=now.strftime('%I:%M %p')
	return render(request,
	    'events/home.html',{
		"name":name,
		"year":year,
		"month":month,
		"month_number": month_number,
		"cal":cal,
		"current_year":current_year,
		"time": time,
		"event_list":event_list,
		})