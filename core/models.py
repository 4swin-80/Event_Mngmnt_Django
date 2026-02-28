from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# =========================
# Custom User Model
# =========================
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('operator', 'Operator'),
        ('customer', 'Customer'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    operator_role = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        help_text="Lighting / Sound / etc."
    )
    status = models.CharField(
        max_length=20,
        default="Active"
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


# =========================
# Event Model
# =========================
class Event(models.Model):

    STATUS_CHOICES = (
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
    )

    name = models.CharField(max_length=100)
    details = models.TextField()  
    price = models.DecimalField(max_digits=10, decimal_places=2)  # NEW
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)  # NEW

    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='events'
    )

    event_status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Scheduled'
    )

    def __str__(self):
        return self.name


# =========================
# Script Model
# =========================
class Script(models.Model):
    SCRIPT_TYPE_CHOICES = (
        ('PDF', 'PDF'),
        ('Audio', 'Audio'),
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='scripts'
    )
    script_name = models.CharField(max_length=100)
    script_type = models.CharField(max_length=20, choices=SCRIPT_TYPE_CHOICES)
    script_file = models.FileField(upload_to='scripts/')

    def __str__(self):
        return self.script_name


# =========================
# Cue Model
# =========================
class Cue(models.Model):
    CUE_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='cues'
    )
    operator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_cues'
    )
    cue_time = models.TimeField()
    cue_action = models.CharField(max_length=100)
    cue_type = models.CharField(max_length=30)
    pre_alert_sec = models.IntegerField(default=0)
    cue_status = models.CharField(
        max_length=30,
        choices=CUE_STATUS_CHOICES,
        default='Pending'
    )

    def __str__(self):
        return f"{self.cue_action} - {self.event.name}"


# =========================
# Attendance Model
# =========================
class Attendance(models.Model):
    STATUS_CHOICES = (
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    )

    operator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='attendance'
    )
    check_in_time = models.DateTimeField(blank=True, null=True)
    check_out_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    def __str__(self):
        return f"{self.operator.username} - {self.event.name}"


# =========================
# Notification Model
# =========================
class Notification(models.Model):
    ALERT_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Triggered', 'Triggered'),
    )

    cue = models.ForeignKey(
        Cue,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    alert_time = models.TimeField()
    alert_message = models.CharField(max_length=150)
    alert_status = models.CharField(
        max_length=20,
        choices=ALERT_STATUS_CHOICES,
        default='Pending'
    )

    def __str__(self):
        return f"Notification for {self.cue.cue_action}"
    
# =========================
# Booking Model
# =========================
class Booking(models.Model):

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    customer_name = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=150, null=True, blank=True)
    mobile = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    event_date = models.DateField(null=True, blank=True)

    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.username} booked {self.event.name}"    
    

# =========================
# Rating Model
# =========================
class Rating(models.Model):
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ratings"
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="ratings"
    )
    stars = models.IntegerField()  # 1 to 5
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.username} - {self.stars} Stars"


# =========================
# Complaint Model
# =========================
class Complaint(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Replied', 'Replied'),
    )

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="complaints"
    )
    subject = models.CharField(max_length=200)
    message = models.TextField()
    admin_reply = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    # 🔔 NEW FIELD
    reply_seen = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint by {self.customer.username}"