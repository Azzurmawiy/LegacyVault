from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import UserSwitchSettings
from core.models import Message

class Command(BaseCommand):
    help = "Runs the Dead Man's Switch check for inactivity and cooling-off release."
    def handle(self, *args, **options):
        now = timezone.now()
        updated = 0
        for s in UserSwitchSettings.objects.select_related("user").all():
            inactive_for = now - s.last_activity_at
            # If active and inactivity exceeded -> start cooling off
            if s.status == "ACTIVE" and inactive_for.days >= s.inactivity_days:
                s.status = "COOLING_OFF"
                s.cooling_started_at = now
                s.save()
                updated += 1
                self.stdout.write(self.style.WARNING(
                    f"{s.user.username}: ACTIVE -> COOLING_OFF"
                ))
            # If cooling off and cooling period passed -> released
            elif s.status == "COOLING_OFF" and s.cooling_started_at:
                cooling_for = now - s.cooling_started_at
                if cooling_for.days >= s.cooling_off_days:
                    s.status = "RELEASED"
                    s.released_at = now
                    s.save()
                    updated += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"{s.user.username}: COOLING_OFF -> RELEASED"
                    ))
                    Message.objects.filter(owner=s.user).update(is_released=True)
        self.stdout.write(self.style.NOTICE(f"Done. Updated {updated} users."))