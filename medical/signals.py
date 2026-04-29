"""
Medical signals — send email alert when a new injury is recorded.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender="medical.Injury")
def injury_created(sender, instance, created, **kwargs):
    """Queue an injury alert email when a new injury is saved."""
    if not created:
        return
    try:
        from django_q.tasks import async_task
        async_task("core.notifications.send_injury_alert", instance.pk)
    except Exception:
        # Fallback: send synchronously if Q cluster isn't running
        from core.notifications import send_injury_alert
        send_injury_alert(instance.pk)
