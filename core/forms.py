from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import Event, Cue, Rating, Complaint

class CueForm(forms.ModelForm):
    class Meta:
        model = Cue
        fields = [
            'event',
            'operator',
            'cue_time',
            'cue_action',
            'cue_type',
            'pre_alert_sec'
        ]
        widgets = {
            'cue_time': forms.TimeInput(attrs={'type': 'time'})
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'date', 'location', 'event_status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['event', 'stars', 'description']
        widgets = {
            'stars': forms.NumberInput(attrs={'min': 1, 'max': 5})
        }


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['subject', 'message']


class AdminReplyForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['admin_reply']      