from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Event, Script, Cue, Attendance, Notification, Booking, Rating, Complaint, Salary


# =========================
# Custom User Admin
# =========================
class CustomUserAdmin(UserAdmin):
    model = User

    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {
            "fields": ("role", "operator_role", "phone", "status"),
        }),
    )

    list_display = (
        "username",
        "email",
        "role",
        "operator_role",
        "status",
        "is_staff",
    )

    list_filter = ("role", "operator_role", "status")


admin.site.register(User, CustomUserAdmin)


# =========================
# Event Admin
# =========================
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "event_status")
    search_fields = ("name",)


# =========================
# Script Admin
# =========================
@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    list_display = ("script_name", "event", "script_type")


# =========================
# Cue Admin
# =========================
@admin.register(Cue)
class CueAdmin(admin.ModelAdmin):
    list_display = (
        "cue_action",
        "event",
        "operator",
        "cue_date",
        "cue_time",
        "cue_status",
        "alert_sent_at",
        "acknowledged_at",
        "escalation_triggered_at",
    )
    list_filter = ("cue_status",)
    search_fields = ("cue_action",)


# =========================
# Attendance Admin
# =========================
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("operator", "event", "status", "check_in_time", "check_out_time")
    list_filter = ("status",)


# =========================
# Notification Admin
# =========================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("cue", "recipient", "notification_type", "alert_time", "alert_status")
    list_filter = ("alert_status", "notification_type")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("customer", "event", "booking_date") 



@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("customer", "event", "stars", "created_at")


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("customer", "subject", "status", "created_at")
    list_editable = ("status",)


@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ("operator", "base_amount", "bonus", "total_amount", "paid_date")    
