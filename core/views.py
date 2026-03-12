from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
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
    linked_heirs_count = FamilyMember.objects.filter(owner=user, claimed_user__isnull=False).count()
    scheduled_count = Message.objects.filter(owner=user, send_date__gt=now).count()
    released_count = Message.objects.filter(owner=user, send_date__lte=now).count()

    context = {
        'memories_count': memories_count,
        'documents_count': documents_count,
        'family_count': family_count,
        'linked_heirs_count': linked_heirs_count,
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
@login_required
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
        form = MessageForm(request.POST, user=request.user)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.owner = request.user
            msg.save()
            messages.success(request, "Message scheduled successfully.")
            return redirect("message")
    else:
        form = MessageForm(user=request.user)

    messages_qs = Message.objects.filter(owner=request.user).order_by("send_date")

    scheduled = [m for m in messages_qs if not m.is_released]
    released = [m for m in messages_qs if m.is_released]
    return render(request, "message.html", {"form": form, "scheduled": scheduled, "released": released})

@login_required
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
def export_data(request):
    """
    Simple JSON export of the current user's data
    (memories, documents metadata, messages, and family members).
    """
    user = request.user

    memories = list(
        Memory.objects.filter(owner=user)
        .order_by("-created_at")
        .values("id", "title", "description", "created_at")
    )
    documents = list(
        Document.objects.filter(owner=user)
        .order_by("-uploaded_at")
        .values("id", "title", "file", "uploaded_at")
    )
    messages_qs = list(
        Message.objects.filter(owner=user)
        .order_by("-send_date")
        .values(
            "id",
            "title",
            "content",
            "send_date",
            "is_released",
            "created_at",
            "recipient_id",
        )
    )
    family = list(
        FamilyMember.objects.filter(owner=user)
        .order_by("name")
        .values(
            "id",
            "name",
            "relation",
            "email",
            "claimed_user_id",
            "created_at",
            "is_active",
        )
    )

    payload = {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
        "memories": memories,
        "documents": documents,
        "messages": messages_qs,
        "family": family,
    }

    return JsonResponse(payload, json_dumps_params={"indent": 2})
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
def heir_portal(request):
    """
    Simple heir portal for the logged-in user.
    Shows all released messages where this user is the recipient.
    """
    recipient = request.user
    messages_list = Message.objects.filter(
        recipient=recipient,
        is_released=True
    ).order_by("-send_date")

    my_invites = FamilyMember.objects.filter(
        claimed_user=recipient,
        is_active=True,
    ).select_related("owner")

    return render(
        request,
        "heir_messages.html",
        {
            "recipient": recipient,
            "messages_list": messages_list,
            "my_invites": my_invites,
        },
    )


def heir_claim(request, token):
    """
    Claim a FamilyMember invite using its token.
    If the user is logged in, we link this invite to their account.
    If not, we let them create an account and then link.
    """
    family_member = get_object_or_404(FamilyMember, invite_token=token, is_active=True)

    # Already claimed: send user to login or portal
    if family_member.claimed_user:
        messages.info(request, "This invite has already been claimed.")
        return redirect("login")

    if request.user.is_authenticated:
        if request.method == "POST":
            family_member.claimed_user = request.user
            family_member.save()
            messages.success(request, "Invite linked to your account. You can now access heir messages.")
            return redirect("heir_portal")

        return render(
            request,
            "heir_claim.html",
            {"family_member": family_member, "mode": "link_existing"},
        )

    # Not authenticated: simple inline signup flow
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "").strip()
        password2 = request.POST.get("password2", "").strip()

        if not username:
            messages.error(request, "Username is required.")
        elif password1 != password2:
            messages.error(request, "Passwords do not match.")
        elif len(password1) < 6:
            messages.error(request, "Password must be at least 6 characters.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "That username has already been taken.")
        else:
            user = User.objects.create_user(
                username=username, email=email, password=password1
            )
            login(request, user)
            family_member.claimed_user = user
            family_member.save()
            messages.success(
                request,
                "Account created and invite claimed. You can now access heir messages.",
            )
            return redirect("heir_portal")

    return render(
        request,
        "heir_claim.html",
        {"family_member": family_member, "mode": "create"},
    )