from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import UserSwitchSettings, Message
from django_q.tasks import async_task
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Checks and updates the status of Legacy Vault dead man switches'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        switches = UserSwitchSettings.objects.all()
        
        updated_to_cooling = 0
        updated_to_released = 0

        for switch in switches:
            if switch.status == "ACTIVE":
                # Check inactivity
                threshold = switch.last_activity_at + timedelta(days=switch.inactivity_days)
                if now >= threshold:
                    switch.status = "COOLING_OFF"
                    switch.cooling_started_at = now
                    switch.save()
                    updated_to_cooling += 1
                    self.stdout.write(self.style.WARNING(f"Switch for {switch.user.username} moved to COOLING_OFF"))

            elif switch.status == "COOLING_OFF":
                # Check cooling off period
                if switch.cooling_started_at is None:
                    # Fallback if somehow missing
                    switch.cooling_started_at = now
                    switch.save()
                    
                threshold = switch.cooling_started_at + timedelta(days=switch.cooling_off_days)
                if now >= threshold:
                    switch.status = "RELEASED"
                    switch.released_at = now
                    switch.save()
                    updated_to_released += 1
                    
                    # Release messages that are due
                    messages_to_release = Message.objects.filter(
                        owner=switch.user,
                        is_released=False,
                        send_date__lte=now
                    )
                    
                    for msg in messages_to_release:
                        msg.is_released = True
                        msg.save()
                        # Enqueue the email task
                        async_task('core.tasks.send_released_message_email', msg.id)
                    
                    released_count = messages_to_release.count()
                    
                    self.stdout.write(self.style.ERROR(f"Switch for {switch.user.username} moved to RELEASED. {released_count} messages released."))

        self.stdout.write(self.style.SUCCESS(f"Successfully processed switches: {updated_to_cooling} cooling off, {updated_to_released} released."))
