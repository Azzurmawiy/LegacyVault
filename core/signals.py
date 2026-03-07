from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import UserSwitchSettings
@receiver(post_save, sender=User)
def create_switch_settings(sender, instance, created, **kwargs):
    if created:
        UserSwitchSettings.objects.create(user=instance, last_activity_at=timezone.now())