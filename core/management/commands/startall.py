import sys
import subprocess
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Start Django server and Cue Engine together"

    def handle(self, *args, **kwargs):

        python = sys.executable  # ensures venv python is used

        self.stdout.write("Starting Django Server...")
        subprocess.Popen([python, "manage.py", "runserver"])

        self.stdout.write("Starting Cue Engine...")
        subprocess.Popen([python, "manage.py", "run_cue_engine"])

        self.stdout.write(self.style.SUCCESS("System Started Successfully"))