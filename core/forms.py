from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from django.utils import timezone
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
        today = timezone.localdate().isoformat()

        self.fields["customer_name"].required = True
        self.fields["location"].required = True
        self.fields["email"].required = True
        self.fields["mobile"].required = True
        self.fields["event_date"].required = True
        self.fields["event_date"].widget.attrs["min"] = today

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control form-control-lg'
            })

    def clean_customer_name(self):
        name = (self.cleaned_data.get("customer_name") or "").strip()
        if not name:
            raise forms.ValidationError("Name is required.")
        return name

    def clean_location(self):
        location = (self.cleaned_data.get("location") or "").strip()
        if not location:
            raise forms.ValidationError("Location is required.")
        return location

    def clean_mobile(self):
        mobile = (self.cleaned_data.get("mobile") or "").strip()
        if not mobile.isdigit() or len(mobile) != 10:
            raise forms.ValidationError("Mobile number must be exactly 10 digits.")
        return mobile

    def clean_event_date(self):
        event_date = self.cleaned_data.get("event_date")
        if event_date and event_date < timezone.localdate():
            raise forms.ValidationError("Event date cannot be in the past.")
        return event_date

class CueForm(forms.ModelForm):

    class Meta:
        model = Cue
        fields = [
            'event',
            'operator',
            'backup_operators',
            'cue_date',
            'cue_time',
            'cue_action',
            'note',
            'pre_alert_sec'
        ]
        widgets = {
            'event': forms.Select(attrs={'class': 'form-select'}),
            'operator': forms.Select(attrs={'class': 'form-select'}),
            'backup_operators': forms.CheckboxSelectMultiple(),
            'cue_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'cue_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'cue_action': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter cue action (e.g., Turn on spotlight)'
            }),
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
        admin_user = kwargs.pop("admin_user", None)
        super().__init__(*args, **kwargs)
        today = timezone.localdate().isoformat()

        self.fields['operator'].queryset = User.objects.filter(role='operator')
        self.fields['backup_operators'].queryset = User.objects.filter(role='operator')
        self.fields['cue_date'].widget.attrs['min'] = today
        if admin_user:
            self.fields["event"].queryset = (
                Event.objects.filter(
                    admin=admin_user,
                    bookings__approval_status="Accepted",
                )
                .distinct()
                .order_by("name")
            )

        self.fields['operator'].label_from_instance = (
            lambda obj: f"{obj.operator_role} - {obj.username}"
        )
        self.fields['backup_operators'].label_from_instance = (
            lambda obj: f"{obj.operator_role} - {obj.username}"
        )
        self.fields['backup_operators'].required = False
        self.fields['backup_operators'].label = "Add Backup operators"

        if event_id:
            self.fields['event'].initial = event_id
            self.fields['event'].widget.attrs['readonly'] = True

    def clean_cue_date(self):
        cue_date = self.cleaned_data.get('cue_date')
        if cue_date and cue_date < timezone.localdate():
            raise forms.ValidationError(
                "Past dates are not allowed. Please select today or a future date."
            )
        return cue_date

    def clean(self):
        cleaned_data = super().clean()
        operator = cleaned_data.get("operator")
        backup_operators = cleaned_data.get("backup_operators")

        if operator and backup_operators and operator in backup_operators:
            self.add_error(
                "backup_operators",
                "Primary operator cannot also be selected as a backup operator."
            )

        return cleaned_data


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter username',
            'autocomplete': 'username'
        })
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter password',
            'autocomplete': 'current-password'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add spacing class to all fields
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': field.widget.attrs.get('class', '') + ' mb-3'
            })

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
    
class CustomerRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove default help texts
        for field in self.fields.values():
            field.help_text = None
            field.widget.attrs.update({
                'class': 'form-control form-control-lg mb-3'
            })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "customer"
        if commit:
            user.save()
        return user
