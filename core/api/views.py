from rest_framework import viewsets

from core.models import (
    Attendance,
    Booking,
    ChatMessage,
    Complaint,
    Cue,
    Event,
    Notification,
    Rating,
    Salary,
    Script,
    User,
)
from core.api.serializers import (
    AttendanceSerializer,
    BookingSerializer,
    ChatMessageSerializer,
    ComplaintSerializer,
    CueSerializer,
    EventSerializer,
    NotificationSerializer,
    RatingSerializer,
    SalarySerializer,
    ScriptSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    search_fields = ["username", "email", "role", "operator_role"]
    ordering_fields = ["id", "username", "role", "status"]


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.select_related("admin").all().order_by("id")
    serializer_class = EventSerializer
    search_fields = ["name", "details", "event_status"]
    ordering_fields = ["id", "name", "price", "event_status"]


class ScriptViewSet(viewsets.ModelViewSet):
    queryset = Script.objects.select_related("event").all().order_by("id")
    serializer_class = ScriptSerializer
    search_fields = ["script_name", "script_type", "event__name"]
    ordering_fields = ["id", "script_name", "script_type"]


class CueViewSet(viewsets.ModelViewSet):
    queryset = (
        Cue.objects.select_related("event", "operator", "acknowledged_by")
        .prefetch_related("backup_operators")
        .all()
        .order_by("cue_date", "cue_time", "id")
    )
    serializer_class = CueSerializer
    search_fields = ["cue_action", "cue_status", "event__name", "operator__username"]
    ordering_fields = ["id", "cue_date", "cue_time", "cue_status"]


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related("operator", "event").all().order_by("id")
    serializer_class = AttendanceSerializer
    search_fields = ["operator__username", "event__name", "status"]
    ordering_fields = ["id", "check_in_time", "check_out_time", "status"]


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.select_related("cue", "recipient").all().order_by("-created_at")
    serializer_class = NotificationSerializer
    search_fields = ["alert_message", "alert_status", "notification_type"]
    ordering_fields = ["id", "alert_time", "created_at", "alert_status"]


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related("customer", "event").all().order_by("-booking_date")
    serializer_class = BookingSerializer
    search_fields = ["customer_name", "location", "mobile", "email", "approval_status"]
    ordering_fields = ["id", "event_date", "booking_date", "approval_status"]


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.select_related("customer", "event").all().order_by("-created_at")
    serializer_class = RatingSerializer
    search_fields = ["customer__username", "event__name", "description"]
    ordering_fields = ["id", "stars", "created_at"]


class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.select_related("customer").all().order_by("-created_at")
    serializer_class = ComplaintSerializer
    search_fields = ["customer__username", "subject", "message", "status"]
    ordering_fields = ["id", "status", "created_at"]


class SalaryViewSet(viewsets.ModelViewSet):
    queryset = Salary.objects.select_related("operator", "attendance").all().order_by("-paid_date")
    serializer_class = SalarySerializer
    search_fields = ["operator__username"]
    ordering_fields = ["id", "base_amount", "bonus", "total_amount", "paid_date"]


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.select_related("sender", "receiver").all().order_by("-created_at")
    serializer_class = ChatMessageSerializer
    search_fields = ["sender__username", "receiver__username", "message"]
    ordering_fields = ["id", "created_at", "is_seen"]
