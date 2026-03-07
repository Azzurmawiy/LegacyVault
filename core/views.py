from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.dateparse import parse_datetime
from django.contrib import messages
from .models import Memory, Document, Message, FamilyMember, UserSwitchSettings
from .forms import MemoryForm, DocumentForm, FamilyMemberForm, MessageForm, UserSwitchSettingsForm
from django.conf import settings
from django.utils import timezone
import os

@login_required
def home(request):
    user = request.user
    now = timezone.now()

    memories_count = Memory.objects.filter(owner=user).count()
    documents_count = Document.objects.filter(owner=user).count()
    family_count = FamilyMember.objects.filter(owner=user).count()
    scheduled_count = Message.objects.filter(owner=user, send_date__gt=now).count()
    released_count = Message.objects.filter(owner=user, send_date__lte=now).count()

    context = {
        'memories_count': memories_count,
        'documents_count': documents_count,
        'family_count': family_count,
        'scheduled_count': scheduled_count,
        'released_count': released_count
    }
    return render(request, 'home.html', context)

@login_required
def memory_list_create(request):
    if request.method == "POST":
        form = MemoryForm(request.POST)
        if form.is_valid():
            memory = form.save(commit=False)
            memory.owner = request.user
            memory.save()
            return redirect('memory')
    else:
        form = MemoryForm()

    memories = Memory.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'memory.html', {'form': form, 'memories': memories})

@login_required
def documents(request):
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.owner = request.user
            doc.save()
            return redirect("documents")
    else:
        form = DocumentForm()

    documents = Document.objects.filter(owner=request.user).order_by('-uploaded_at')
    return render(request, "documents.html", {"form": form, "documents": documents})
def document_delete(request, pk):
    doc = get_object_or_404(Document, pk=pk, owner=request.user)

    if request.method == "POST":
        #delete file from media folder
        if doc.file and os.path.isfile(doc.file.path):
            os.remove(doc.file.path)

        doc.delete()
        return redirect("documents")
    
    return render(request, "document_delete.html", {"doc": doc})

@login_required
def message(request):
    user = request.user
    now = timezone.now()
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.owner = request.user
            msg.save()
            messages.success(request, "Message scheduled successfully.")
            return redirect("message")
    else:
        form = MessageForm()

    messages_qs = Message.objects.filter(owner=request.user).order_by("send_date")

    scheduled = [m for m in messages_qs if not m.is_released()]
    released = [m for m in messages_qs if m.is_released()]
    return render(request, "message.html", {"form": form, "scheduled": scheduled, "released": released})

def family(request):
    if request.method == "POST":
       form = FamilyMemberForm(request.POST)
       if form.is_valid():
        member = form.save(commit=False)
        member.owner = request.user
        member.save()
        messages.success(request, "Family member added.")
        return redirect("family")
    else:
        form = FamilyMemberForm()
    members = FamilyMember.objects.filter(owner=request.user).order_by("name")
    return render(request, "family.html", {"form": form, "members": members})
@login_required
def memory_update(request, pk):
    memory = get_object_or_404(Memory, pk=pk, owner=request.user)

    if request.method == "POST":
        form = MemoryForm(request.POST, instance=memory)
        if form.is_valid():
            form.save()
            return redirect('memory')
    else:
        form = MemoryForm(instance=memory)

    return render(request, 'memory_edit.html', {'form': form, 'memory': memory})
@login_required
def memory_delete(request, pk):
    memory = get_object_or_404(Memory, pk=pk, owner=request.user)

    if request.method == "POST":
        memory.delete()
        return redirect('memory')

    return render(request, 'memory_delete.html', {'memory': memory})

@login_required
def switch_settings(request):
    settings_obj, _ = UserSwitchSettings.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserSwitchSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Switch settings updated successfully.")
            return redirect("switch_settings")
    else:
        form = UserSwitchSettingsForm(instance=settings_obj)

    return render(request, "switch_settings.html", {"form": form, "settings_obj": settings_obj})
@login_required
def heir_messages(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)

    messages_list = Message.objects.filter(recipient=recipient, is_released=True).order_by("-send_date")

    return render(request, "heir_messages.html", {"recipient":recipient, "messages_list": messages_list,})