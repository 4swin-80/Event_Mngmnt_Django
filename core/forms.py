from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control form-control-lg'
            })

class CueForm(forms.ModelForm):

    class Meta:
        model = Cue
        fields = [
            'event',
            'operator',
            'cue_date',
            'cue_time',
            'cue_action',
            'note',
            'pre_alert_sec'
        ]
        widgets = {
            'event': forms.Select(attrs={'class': 'form-select'}),
            'operator': forms.Select(attrs={'class': 'form-select'}),
            'cue_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'cue_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'cue_action': forms.Select(attrs={'class': 'form-select'}),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'pre_alert_sec': forms.NumberInput(attrs={
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        event_id = kwargs.pop('event_id', None)
        super().__init__(*args, **kwargs)

        self.fields['operator'].queryset = User.objects.filter(role='operator')

        self.fields['operator'].label_from_instance = (
            lambda obj: f"{obj.operator_role} - {obj.username}"
        )

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
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['stars', 'description']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your review...'
            })
        } 


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your issue...'
            })
        }


class AdminReplyForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['admin_reply']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['admin_reply'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Write your reply here...'
        })  



class CustomerRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "customer"  # 🔥 force role
        if commit:
            user.save()
        return user