from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from .automation import check_and_trigger_cues
from .forms import CueForm
from .models import Cue, Event, Notification, User


class CueFormTests(TestCase):
    def test_primary_operator_cannot_be_selected_as_backup(self):
        admin = User.objects.create_user(
            username="admin1",
            password="pass123",
            role="admin",
        )
        primary_operator = User.objects.create_user(
            username="primary",
            password="pass123",
            role="operator",
            operator_role="lighting",
        )
        event = Event.objects.create(
            name="Launch Event",
            details="Details",
            price=1000,
            admin=admin,
        )

        form = CueForm(
            data={
                "event": event.id,
                "operator": primary_operator.id,
                "backup_operators": [primary_operator.id],
                "cue_date": timezone.localdate().isoformat(),
                "cue_time": "10:00",
                "cue_action": "Turn on spotlight",
                "note": "",
                "pre_alert_sec": 0,
            },
            admin_user=admin,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("backup_operators", form.errors)


class CueAutomationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin1",
            password="pass123",
            role="admin",
        )
        self.primary_operator = User.objects.create_user(
            username="primary",
            password="pass123",
            role="operator",
            operator_role="lighting",
        )
        self.backup_operator_1 = User.objects.create_user(
            username="backup1",
            password="pass123",
            role="operator",
            operator_role="sound",
        )
        self.backup_operator_2 = User.objects.create_user(
            username="backup2",
            password="pass123",
            role="operator",
            operator_role="stage",
        )
        self.event = Event.objects.create(
            name="Annual Event",
            details="Details",
            price=2000,
            admin=self.admin,
        )

    def test_escalates_to_all_backup_operators_and_admin_after_30_seconds(self):
        now = timezone.localtime()
        cue = Cue.objects.create(
            event=self.event,
            operator=self.primary_operator,
            cue_date=now.date(),
            cue_time=(now - timedelta(minutes=1)).time().replace(microsecond=0),
            cue_action="Trigger opening lights",
            pre_alert_sec=0,
        )
        cue.backup_operators.add(self.backup_operator_1, self.backup_operator_2)

        sent_alerts = []

        class FakeChannelLayer:
            def group_send(self, group_name, payload):
                sent_alerts.append((group_name, payload))

        with patch("core.automation.get_channel_layer", return_value=FakeChannelLayer()):
            with patch("core.automation.async_to_sync", side_effect=lambda func: func):
                with patch("core.automation.timezone.localtime", return_value=now):
                    check_and_trigger_cues()

                cue.refresh_from_db()
                self.assertIsNotNone(cue.alert_sent_at)
                self.assertIsNone(cue.escalation_triggered_at)
                self.assertEqual(
                    Notification.objects.filter(
                        cue=cue,
                        notification_type="primary",
                        recipient=self.primary_operator,
                    ).count(),
                    1,
                )
                self.assertEqual(len(sent_alerts), 1)

                sent_alerts.clear()
                escalation_time = cue.alert_sent_at + timedelta(seconds=31)

                with patch("core.automation.timezone.localtime", return_value=escalation_time):
                    check_and_trigger_cues()

        cue.refresh_from_db()
        self.assertIsNotNone(cue.escalation_triggered_at)
        self.assertEqual(
            Notification.objects.filter(
                cue=cue,
                notification_type="backup",
            ).count(),
            2,
        )
        self.assertEqual(
            Notification.objects.filter(
                cue=cue,
                notification_type="admin",
                recipient=self.admin,
            ).count(),
            1,
        )
        self.assertEqual(len(sent_alerts), 2)

    def test_acknowledged_cue_does_not_escalate(self):
        now = timezone.localtime()
        cue = Cue.objects.create(
            event=self.event,
            operator=self.primary_operator,
            cue_date=now.date(),
            cue_time=(now - timedelta(minutes=1)).time().replace(microsecond=0),
            cue_action="Start music",
            pre_alert_sec=0,
            alert_sent_at=now - timedelta(seconds=31),
            acknowledged_at=now - timedelta(seconds=10),
            acknowledged_by=self.primary_operator,
        )
        cue.backup_operators.add(self.backup_operator_1)

        class FakeChannelLayer:
            def group_send(self, group_name, payload):
                raise AssertionError("No live alerts should be sent after acknowledgment.")

        with patch("core.automation.get_channel_layer", return_value=FakeChannelLayer()):
            with patch("core.automation.async_to_sync", side_effect=lambda func: func):
                with patch("core.automation.timezone.localtime", return_value=now):
                    check_and_trigger_cues()

        cue.refresh_from_db()
        self.assertIsNone(cue.escalation_triggered_at)
        self.assertFalse(Notification.objects.filter(cue=cue, notification_type="admin").exists())

    def test_backup_operator_cannot_acknowledge_escalated_cue(self):
        cue = Cue.objects.create(
            event=self.event,
            operator=self.primary_operator,
            cue_date=timezone.localdate(),
            cue_time=timezone.localtime().time().replace(microsecond=0),
            cue_action="Backup take-over cue",
            pre_alert_sec=0,
            escalation_triggered_at=timezone.now(),
        )
        cue.backup_operators.add(self.backup_operator_1)

        self.client.force_login(self.backup_operator_1)
        response = self.client.get(f"/complete-cue/{cue.id}/")

        self.assertEqual(response.status_code, 404)

        cue.refresh_from_db()
        self.assertEqual(cue.cue_status, "Pending")
        self.assertIsNone(cue.acknowledged_by)
        self.assertIsNone(cue.acknowledged_at)


class NotificationViewTests(TestCase):
    def test_admin_notifications_are_marked_seen_when_opened(self):
        admin = User.objects.create_user(
            username="admin_notify",
            password="pass123",
            role="admin",
        )
        operator = User.objects.create_user(
            username="operator_notify",
            password="pass123",
            role="operator",
            operator_role="lighting",
        )
        event = Event.objects.create(
            name="Seen State Event",
            details="Details",
            price=1500,
            admin=admin,
        )
        cue = Cue.objects.create(
            event=event,
            operator=operator,
            cue_date=timezone.localdate(),
            cue_time=timezone.localtime().time().replace(microsecond=0),
            cue_action="Notify admin",
            pre_alert_sec=0,
        )
        notification = Notification.objects.create(
            cue=cue,
            recipient=admin,
            notification_type="admin",
            alert_time=cue.cue_time,
            alert_message="Operator missed cue",
            alert_status="Triggered",
            is_seen=False,
        )

        self.client.force_login(admin)
        response = self.client.get("/notifications/")

        self.assertEqual(response.status_code, 200)
        notification.refresh_from_db()
        self.assertTrue(notification.is_seen)
