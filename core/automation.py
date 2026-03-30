from datetime import datetime, timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from .models import Cue, Notification


def send_live_alert(channel_layer, user_id, message):
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "send_alert",
            "message": message,
        }
    )


def check_and_trigger_cues():
    now = timezone.localtime()
    cues = Cue.objects.filter(cue_status="Pending").prefetch_related("backup_operators")
    channel_layer = get_channel_layer()

    for cue in cues:
        cue_datetime = datetime.combine(cue.cue_date, cue.cue_time)
        cue_datetime = timezone.make_aware(
            cue_datetime,
            timezone.get_current_timezone()
        )
        alert_datetime = cue_datetime - timedelta(seconds=cue.pre_alert_sec)

        if now < alert_datetime:
            continue

        if cue.alert_sent_at is None:
            Notification.objects.create(
                cue=cue,
                recipient=cue.operator,
                notification_type="primary",
                alert_time=cue.cue_time,
                alert_message=f"Action: {cue.cue_action}",
                alert_status="Triggered",
            )
            send_live_alert(channel_layer, cue.operator.id, f"{cue.cue_action} NOW!")
            cue.alert_sent_at = now
            cue.save(update_fields=["alert_sent_at"])
            continue

        if cue.acknowledged_at is not None or cue.escalation_triggered_at is not None:
            continue

        if now < cue.alert_sent_at + timedelta(seconds=30):
            continue

        backup_operators = list(cue.backup_operators.all())
        if not backup_operators:
            continue

        missed_message = (
            f"{cue.operator.username} missed this cue. Backup action required: "
            f"{cue.cue_action}"
        )

        for backup_operator in backup_operators:
            Notification.objects.create(
                cue=cue,
                recipient=backup_operator,
                notification_type="backup",
                alert_time=cue.cue_time,
                alert_message=missed_message,
                alert_status="Triggered",
            )
            send_live_alert(channel_layer, backup_operator.id, missed_message)

        Notification.objects.create(
            cue=cue,
            recipient=cue.event.admin,
            notification_type="admin",
            alert_time=cue.cue_time,
            alert_message=(
                f"{cue.operator.username} missed cue '{cue.cue_action}'. "
                f"Backup operators have been notified."
            ),
            alert_status="Triggered",
        )

        cue.escalation_triggered_at = now
        cue.save(update_fields=["escalation_triggered_at"])
