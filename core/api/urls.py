from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.api.views import (
    AttendanceViewSet,
    BookingViewSet,
    ChatMessageViewSet,
    ComplaintViewSet,
    CueViewSet,
    EventViewSet,
    NotificationViewSet,
    RatingViewSet,
    SalaryViewSet,
    ScriptViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("events", EventViewSet)
router.register("scripts", ScriptViewSet)
router.register("cues", CueViewSet)
router.register("attendance", AttendanceViewSet)
router.register("notifications", NotificationViewSet)
router.register("bookings", BookingViewSet)
router.register("ratings", RatingViewSet)
router.register("complaints", ComplaintViewSet)
router.register("salaries", SalaryViewSet)
router.register("chat-messages", ChatMessageViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
