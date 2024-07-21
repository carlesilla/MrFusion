from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.core.files.images import get_image_dimensions
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from app.forms import CreateChatForm, UpdateChatMembersForm, EditChatForm
from app import mediator
from app.models import Chat, ChatHistory, ConflictInfo, Question, UserProfile
from app.views import views_utils

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import datetime
from io import BytesIO
import json
import os
from PIL import Image as PilImage
import random
import string
import time
import uuid as uuid_generator



def index(request):
    if request.user.is_authenticated:
        context = views_utils.get_context(request)
        context["section"] = "chats"

        return render(request, "home.html", context)
    else:
        return redirect("login_view")


@login_required
def chat(request, uuid):
    context = views_utils.get_context(request)
    context["section"] = "chats"
    if Chat.objects.filter(uuid=uuid, members=request.user).exists():
        chat = Chat.objects.get(uuid=uuid, members=request.user)

        update_chat_members_form = UpdateChatMembersForm()
        initial = {"name":chat.name, "description":chat.description}
        edit_chat_form = EditChatForm(initial=initial)
        context["chat"] = chat
        chat_history = ChatHistory.objects.filter(chat=chat).order_by("created_at")
        context["chat_history"] = chat_history
        context["update_chat_members_form"] = update_chat_members_form
        context["edit_chat_form"] = edit_chat_form
        return render(request, "chat.html", context = context)
    elif request.user.is_superuser:
        chat = Chat.objects.get(uuid=uuid)

        update_chat_members_form = UpdateChatMembersForm()
        initial = {"name":chat.name, "description":chat.description}
        edit_chat_form = EditChatForm(initial=initial)
        context["chat"] = chat
        chat_history = ChatHistory.objects.filter(chat=chat).order_by("created_at")
        context["chat_history"] = chat_history
        context["update_chat_members_form"] = update_chat_members_form
        context["edit_chat_form"] = edit_chat_form

        return render(request, "chat.html", context = context)
    else:
        messages.add_message(request, messages.ERROR, "Chat doesn't exist")
        return redirect("index")


@login_required
def create_chat(request):
    if request.method == "POST":
        form = CreateChatForm(request.POST, request.FILES)
        contacts = User.objects.all()
        choices = []
        for contact in contacts:
            choices.append((contact.id, contact.id))

        form.fields["members"].choices = choices

        if form.is_valid():
            name = form.cleaned_data["name"]
            description = form.cleaned_data["description"]
            member_ids = form.cleaned_data["members"]
            uuid = str(uuid_generator.uuid4())
            permalink = slugify(name)
            members = User.objects.filter(id__in=member_ids)
            chat = Chat.objects.create(
                uuid = uuid,
                permalink = permalink,
                name = name,
                description = description,
                owner = request.user
            )
            for member in members:
                chat.members.add(member)

            messages.add_message(request, messages.INFO, "Chat created")
            
        else:
            print(form)
    return redirect("index")


@login_required
def edit_chat(request, uuid):
    if request.method == "POST":
        form = EditChatForm(request.POST)
        if form.is_valid():
            chat = Chat.objects.get(uuid=uuid)
            name = form.cleaned_data["name"]
            description = form.cleaned_data["description"]
            chat.name = name
            chat.description = description
            chat.save()
            messages.add_message(request, messages.INFO, "Chat updated")
        else:
            messages.add_message(request, messages.ERROR, "Error updating chat")
    return redirect("index")


@login_required
def update_chat_members(request, uuid):
    if request.method == "POST":
        form = UpdateChatMembersForm(request.POST)
        contacts = User.objects.all()
        choices = []
        for contact in contacts:
            choices.append((contact.id, contact.id))

        form.fields["members"].choices = choices
        
        if form.is_valid():
            chat = Chat.objects.get(uuid=uuid)
            updated_member_ids = form.cleaned_data["members"]
            updated_members = User.objects.filter(id__in=updated_member_ids)
            # Add new ones
            for member in updated_members:
                if member not in chat.members.all():
                    chat.members.add(member)
                    messages.add_message(request, messages.INFO, member.first_name + " has been added to the chat")
            # Remove the rest
            for member in chat.members.all():
                if (chat.owner == member) and (member not in updated_members):
                    messages.add_message(request, messages.ERROR, member.first_name + " can not be removed from the chat")
                elif member not in updated_members:
                    chat.members.remove(member)
                    messages.add_message(request, messages.INFO, member.first_name + " has been removed from the chat")
        else:
            messages.add_message(request, messages.ERROR, "Error updating chat members")
    return redirect("index")



@login_required
def delete_chat(request, uuid):
    chat = Chat.objects.get(uuid=uuid)
    if chat.owner == request.user:
        chat.delete()
        messages.add_message(request, messages.INFO, "Chat deleted")
    else:
        messages.add_message(request, messages.ERROR, "Only the owner of the Chat can delete it")

    return redirect("/")


@login_required
def empty_chat(request, uuid):
    chat = Chat.objects.get(uuid=uuid)
    if chat.owner == request.user:
        ChatHistory.objects.filter(chat=chat).delete()
        messages.add_message(request, messages.INFO, "Chat messages deleted")
    else:
        messages.add_message(request, messages.ERROR, "Only the owner of the Chat can delete the messages")

    return redirect("/")



@login_required
def leave_chat(request, uuid):
    chat = Chat.objects.get(uuid=uuid)
    chat.members.remove(request.user)
    messages.add_message(request, messages.INFO, "You have left the chat")
    return redirect("/")
