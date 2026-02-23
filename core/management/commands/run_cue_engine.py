from django.core.management.base import BaseCommand
import time
from core.automation import check_and_trigger_cues


class Command(BaseCommand):
    help = "Runs Cue Automation Engine"

    def handle(self, *args, **kwargs):
        self.stdout.write("Cue Engine Started...")
        while True:
            check_and_trigger_cues()
            time.sleep(10)