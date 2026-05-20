from rest_framework import serializers

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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "operator_role",
            "phone",
            "status",
            "is_staff",
        ]
        read_only_fields = ["is_staff"]


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "details",
            "price",
            "image",
            "admin",
            "event_status",
        ]


class ScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Script
        fields = [
            "id",
            "event",
            "script_name",
            "script_type",
            "script_file",
        ]


class CueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cue
        fields = [
            "id",
            "event",
            "operator",
            "backup_operators",
            "cue_date",
            "cue_time",
            "cue_action",
            "note",
            "pre_alert_sec",
            "alert_sent_at",
            "acknowledged_at",
            "acknowledged_by",
            "escalation_triggered_at",
            "cue_status",
        ]


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = [
            "id",
            "operator",
            "event",
            "check_in_time",
            "check_out_time",
            "status",
        ]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "cue",
            "recipient",
            "notification_type",
            "alert_time",
            "alert_message",
            "alert_status",
            "created_at",
            "is_seen",
        ]
        read_only_fields = ["created_at"]


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "customer",
            "event",
            "customer_name",
            "location",
            "mobile",
            "email",
            "event_date",
            "approval_status",
            "admin_action_at",
            "customer_notified",
            "booking_date",
        ]
        read_only_fields = ["booking_date"]


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = [
            "id",
            "customer",
            "event",
            "stars",
            "description",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = [
            "id",
            "customer",
            "subject",
            "message",
            "admin_reply",
            "status",
            "reply_seen",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class SalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Salary
        fields = [
            "id",
            "operator",
            "attendance",
            "base_amount",
            "bonus",
            "total_amount",
            "paid_date",
        ]
        read_only_fields = ["paid_date"]


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "sender",
            "receiver",
            "message",
            "is_seen",
            "created_at",
        ]
        read_only_fields = ["created_at"]
