from django import forms
from .models import Memory, Document, FamilyMember, Message, UserSwitchSettings
from django.utils import timezone

class MemoryForm(forms.ModelForm):
    class Meta:
        model = Memory
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control soft-input', 'placeholder': 'Memory title'}),
            'description': forms.Textarea(attrs={'class': 'form-control soft-input', 'rows': 5, 'placeholder': 'Write your memory...'}),
        }

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control soft-input', 'placeholder': 'Document title'})
        }

class FamilyMemberForm(forms.ModelForm):
    class Meta:
        model = FamilyMember
        fields = ['name', 'relation', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control soft-input', 'placeholder': 'Family member name'}),
            'relation': forms.TextInput(attrs={'class': 'form-control soft-input', 'placeholder': 'Relation'}),
            'email': forms.EmailInput(attrs={'class': 'form-control soft-input', 'placeholder': 'Email (optional)'}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['title', 'content', 'send_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control soft-input', 'placeholder': 'Message title'}),
            'content': forms.Textarea(attrs={'class': 'form-control soft-input', 'rows': 4, 'placeholder': 'Write your message...'}),
            'released_date': forms.DateTimeInput(attrs={'class': 'form-control soft-input', 'type': 'datetime-local'}),
            'type': 'datetime-local',
            'class': 'form-control soft-input',
            'recipient': forms.Select(attrs={'class': 'form-control soft-input'})
        }

    def clean_released_date(self):
        released_date = self.cleaned_data.get('released_date')
        if released_date and released_date < timezone.now():
            raise forms.ValidationError("Release date cannot be in the past.")
        return released_date

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control soft-input', 'placeholder': 'Document title'})
        }

class UserSwitchSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSwitchSettings
        fields = ['inactivity_days', 'cooling_off_days']
        widgets = {
            'inactivity_days': forms.NumberInput(attrs={
                'class': 'form-control soft-input',
                'min': 1
            }),
            'cooling_off_days': forms.NumberInput(attrs={
                'class': 'form-control soft-input',
                'min': 0
            }),
        }