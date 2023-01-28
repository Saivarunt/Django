from django import forms
from django.forms import ModelForm
from .models import Venue,Event 

class VenueForm(ModelForm):
	class Meta:
		model=Venue
		# fields="__all__"
		fields=('name','address','zip_code','phone','web','email_address','venue_image')
		labels={
		'name':"",
		'address':"",
		'zip_code':"",
		'phone':"",
		'web':"",
		'email_address':"",
		'venue_image':"",
		}
		widgets={
		'name':forms.TextInput(attrs={'class':'form-control','placeholder':'Venue'}),
		'address':forms.TextInput(attrs={'class':'form-control','placeholder':'Address'}),
		'zip_code':forms.TextInput(attrs={'class':'form-control','placeholder':'Zip code'}),
		'phone':forms.TextInput(attrs={'class':'form-control','placeholder':'Phone'}),
		'web':forms.TextInput(attrs={'class':'form-control','placeholder':'Web'}),
		'email_address':forms.TextInput(attrs={'class':'form-control','placeholder':'Email'}),
		}

#admin super user event form
class EventFormAdmin(ModelForm):
	class Meta:
		model=Event
		# fields="__all__"
		fields=('name','event_date','venue','manager','attendees','description')
		labels={
		'name':"",
		'event_date':"YYYY-MM-DD HH:MM:SS",
		'venue':"Venue",
		'manager':"Manager",
		'attendees':"Attendees",
		'description':"",

		}
		widgets={
		'name':forms.TextInput(attrs={'class':'form-control','placeholder':'Event'}),
		'event_date':forms.TextInput(attrs={'class':'form-control','placeholder':'Date'}),
		'venue':forms.Select(attrs={'class':'form-select','placeholder':'Venue'}),
		'manager':forms.Select(attrs={'class':'form-select','placeholder':'Manager'}),
		'attendees':forms.SelectMultiple(attrs={'class':'form-control','placeholder':'Attendees'}),
		'description':forms.Textarea(attrs={'class':'form-control','placeholder':'Desc'}),
		
		}

#user event form
class EventForm(ModelForm):
	class Meta:
		model=Event
		# fields="__all__"
		fields=('name','event_date','venue','attendees','description')
		labels={
		'name':"",
		'event_date':"YYYY-MM-DD HH:MM:SS",
		'venue':"Venue",
		'attendees':"Attendees",
		'description':"",

		}
		widgets={
		'name':forms.TextInput(attrs={'class':'form-control','placeholder':'Event'}),
		'event_date':forms.TextInput(attrs={'class':'form-control','placeholder':'Date'}),
		'venue':forms.Select(attrs={'class':'form-select','placeholder':'Venue'}),
		'attendees':forms.SelectMultiple(attrs={'class':'form-control','placeholder':'Attendees'}),
		'description':forms.Textarea(attrs={'class':'form-control','placeholder':'Desc'}),
		
		}