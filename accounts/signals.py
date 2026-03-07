from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from core.models import UserSwitchSettings


@receiver(user_logged_in)
def update_heartbeat(sender, user, request, **kwargs):
    settings, _ = UserSwitchSettings.objects.get_or_create(user=user)
    settings.last_activity_at = timezone.now()
    settings.save()