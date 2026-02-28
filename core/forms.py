from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import Event, Cue, Rating, Complaint, Booking, User


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'customer_name',
            'location',
            'mobile',
            'email',
            'event_date'
        ]
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'})
        }

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

    def __init__(self, *args, **kwargs):
        event_id = kwargs.pop('event_id', None)
        super().__init__(*args, **kwargs)

        # ✅ Show only operators
        self.fields['operator'].queryset = User.objects.filter(role='operator')

        # ✅ Show operator role in dropdown
        self.fields['operator'].label_from_instance = (
            lambda obj: f"{obj.operator_role} - {obj.username}"
        )

        # ✅ Auto-select event if provided
        if event_id:
            self.fields['event'].initial = event_id
            self.fields['event'].widget.attrs['readonly'] = True


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
        fields = ['name', 'details', 'price', 'image']


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['stars', 'description']  


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['subject', 'message']


class AdminReplyForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['admin_reply']      