from django.utils import timezone
from .models import Cue, Notification, Attendance
from datetime import datetime, timedelta
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def check_and_trigger_cues():
    now = timezone.localtime()

    cues = Cue.objects.filter(cue_status="Pending")

    channel_layer = get_channel_layer()

    for cue in cues:
        # Combine today's date with cue_time
        cue_datetime = datetime.combine(
            now.date(),
            cue.cue_time
        )

        # Subtract pre alert seconds
        alert_datetime = cue_datetime - timedelta(seconds=cue.pre_alert_sec)

        # If current time reached alert time
        if now >= alert_datetime:

            # Avoid duplicate notifications
            if not Notification.objects.filter(cue=cue, alert_status="Triggered").exists():

                # Create notification
                Notification.objects.create(
                    cue=cue,
                    alert_time=cue.cue_time,
                    alert_message=f"Action: {cue.cue_action}",
                    alert_status="Triggered"
                )

                # 🔥 AUTO ATTENDANCE
                Attendance.objects.get_or_create(
                    operator=cue.operator,
                    event=cue.event,
                    defaults={
                        "check_in_time": timezone.now(),
                        "status": "Present"
                    }
                )

                # 🔥 SEND REAL-TIME WEBSOCKET ALERT
                async_to_sync(channel_layer.group_send)(
                    f"user_{cue.operator.id}",
                    {
                        "type": "send_alert",
                        "message": f"🚨 {cue.cue_action} NOW!"
                    }
                )