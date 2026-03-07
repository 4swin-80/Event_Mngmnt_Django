from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_chatmessage"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="admin_action_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="booking",
            name="approval_status",
            field=models.CharField(
                choices=[("Pending", "Pending"), ("Accepted", "Accepted"), ("Rejected", "Rejected")],
                default="Pending",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="booking",
            name="customer_notified",
            field=models.BooleanField(default=True),
        ),
    ]
