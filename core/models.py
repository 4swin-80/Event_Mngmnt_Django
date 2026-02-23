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
    date = models.DateField()
    location = models.CharField(max_length=100)
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