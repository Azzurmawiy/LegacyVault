from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
import uuid


class Memory(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memories')
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Document(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE,related_name='documents')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Message(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    recipient = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True, related_name='received_legacy_messages')
    title = models.CharField(max_length=200)
    content = models.TextField()
    send_date = models.DateTimeField(default=timezone.now)
    is_released = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class FamilyMember(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="family_members"
    )
    name = models.CharField(max_length=200)
    relation = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    # Future-proofing for inheritance system
    claimed_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="claimed_family_profiles"
    )
    invite_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class UserSwitchSettings(models.Model):
    STATUS_CHOICES = (
        ("ACTIVE", "Active"),
        ("COOLING_OFF", "Cooling Off"),
        ("RELEASED", "Released"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="switch")
    inactivity_days = models.PositiveIntegerField(default=30)
    cooling_off_days = models.PositiveIntegerField(default=7)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE")
    last_activity_at = models.DateTimeField(default=timezone.now)
    cooling_started_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.user.username} Switch ({self.status})"