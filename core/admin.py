from django.contrib import admin
from .models import Memory, Document, Message, FamilyMember, UserSwitchSettings
from django.utils import timezone
from datetime import timedelta

class UserSwitchSettingsAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # Only for new objects
            form.base_fields['status'].initial = 'COOLING_OFF'
            form.base_fields['cooling_started_at'].initial = timezone.now() - timedelta(days=30)  # old date, say 30 days ago
            form.base_fields['cooling_off_days'].initial = 0
        return form

admin.site.register(Memory)
admin.site.register(Document)
admin.site.register(Message)
admin.site.register(FamilyMember)
admin.site.register(UserSwitchSettings, UserSwitchSettingsAdmin)