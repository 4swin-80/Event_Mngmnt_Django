from django.utils import timezone
from datetime import datetime, timedelta
from .models import Cue, Notification, Attendance
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def check_and_trigger_cues():
    now = timezone.localtime()
    cues = Cue.objects.filter(cue_status="Pending")
    channel_layer = get_channel_layer()

    for cue in cues:

        cue_datetime = datetime.combine(
            cue.cue_date,
            cue.cue_time
        )

        cue_datetime = timezone.make_aware(
            cue_datetime,
            timezone.get_current_timezone()
        )

        alert_datetime = cue_datetime - timedelta(
            seconds=cue.pre_alert_sec
        )

        if now >= alert_datetime:

            if not Notification.objects.filter(
                cue=cue,
                alert_status="Triggered"
            ).exists():

                Notification.objects.create(
                    cue=cue,
                    alert_time=cue.cue_time,
                    alert_message=f"Action: {cue.cue_action}",
                    alert_status="Triggered"
                )

                async_to_sync(channel_layer.group_send)(
                    f"user_{cue.operator.id}",
                    {
                        "type": "send_alert",
                        "message": f"🚨 {cue.cue_action} NOW!"
                    }
                )

                # Optional: mark cue completed
                cue.cue_status = "Completed"
                cue.save()