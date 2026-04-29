"""
Management command: send the daily digest email immediately.

Usage:
    python manage.py send_digest
    python manage.py send_digest --schedule   # also registers the daily Q schedule
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Send the daily ApexForge digest email to all managers."

    def add_arguments(self, parser):
        parser.add_argument(
            "--schedule",
            action="store_true",
            help="Register (or update) the daily Q schedule after sending.",
        )

    def handle(self, *args, **options):
        self.stdout.write("Sending daily digest...")
        from core.notifications import send_daily_digest
        send_daily_digest()
        self.stdout.write(self.style.SUCCESS("Daily digest sent OK."))

        if options["schedule"]:
            self._register_schedule()

    def _register_schedule(self):
        from django_q.models import Schedule
        from django_q.tasks import schedule as q_schedule

        name = "daily_digest"
        if Schedule.objects.filter(name=name).exists():
            self.stdout.write("Schedule already exists — skipping.")
            return

        q_schedule(
            "core.notifications.send_daily_digest",
            name=name,
            schedule_type=Schedule.DAILY,
            minutes=None,
            hour=7,   # 07:00 server time
        )
        self.stdout.write(self.style.SUCCESS("Daily digest scheduled at 07:00."))
