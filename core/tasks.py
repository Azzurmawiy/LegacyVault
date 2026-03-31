from django.core.mail import send_mail
from django.conf import settings
from .models import Message

def send_released_message_email(message_id):
    try:
        message = Message.objects.get(id=message_id)
        if not message.is_released:
            # Should not happen if called correctly, but safety first
            return False
            
        recipient_email = None
        if message.recipient and message.recipient.email:
            recipient_email = message.recipient.email
        
        if not recipient_email:
            # If no recipient email, we might want to look at family members
            # or just log it. For now, we'll assume recipient has email.
            return False

        subject = f"Legacy Message: {message.title}"
        body = f"You have received a legacy message from {message.owner.username}:\n\n{message.content}"
        
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
        return True
    except Message.DoesNotExist:
        return False
    except Exception as e:
        # Log error
        print(f"Error sending email: {e}")
        return False
