from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
#from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
#from django.core.management import call_command
from django.core import management
from django.http import HttpResponse
from django.shortcuts import render, redirect


from app import mediator
from app.forms import UploadProfilePicForm, ProfileSettingsForm, ChangePasswordForm, UploadBackupFileForm
from app.models import Chat, ChatHistory, ConflictInfo, Context, InvitationToken, Question, UserProfile
from app.views import views_utils


import datetime
from io import BytesIO, StringIO
import json
import os
from PIL import Image as PilImage



@login_required
def change_profile_settings(request):
    if request.method == "POST":
        form = ProfileSettingsForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            is_party = form.cleaned_data["is_party"]

            user = request.user
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()
            user.user_profile.is_party = is_party
            user.user_profile.save()

            messages.add_message(request, messages.INFO, "Profile settings updated successfully")
        else:
            messages.add_message(request, messages.ERROR, "An error has occurred, please check the fields and try again.")

    return redirect("index")



@login_required
def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            current_password = form.cleaned_data["current_password"]
            new_password = form.cleaned_data["new_password"]
            confirm_password = form.cleaned_data["confirm_password"]

            if new_password != confirm_password:
                messages.add_message(request, messages.ERROR, "Passwords don't match")
            else:
                user = authenticate(request, username=request.user.username, password=current_password)
                if user is None:
                    messages.add_message(request, messages.ERROR, "Wrong password")
                else:
                    user = request.user
                    user.set_password(new_password)
                    user.save()
                    messages.add_message(request, messages.INFO, "Password has been successfully changed")
        else:
            messages.add_message(request, messages.ERROR, "An error has occurred, please check the fields and try again.")

    return redirect("index")


@user_passes_test(lambda u: u.is_superuser)
def backup(request):
    buf = StringIO()
    management.call_command("dumpdata", "--natural-foreign", "--natural-primary", "-e", "contenttypes", "-e", "auth.Permission", "--indent", "2", stdout=buf)

    data = buf.getvalue()
    response = HttpResponse(data, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=backup.json'
    return response


@user_passes_test(lambda u: u.is_superuser)
def restore(request):
    if request.method == "POST":
        form = UploadBackupFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data.get("backup_file")
            folder='backup/'
            fs = FileSystemStorage(location=folder)
            file_name = fs.save(file.name, file)
            file_path = os.path.join(settings.BASE_DIR, 'backup/')
            management.call_command("loaddata", file_path + file_name)
        else:
            print(form)

    return redirect("index")



def resize_uploaded_image(image, max_width, max_height):
    size = (max_width, max_height)

    # Uploaded file is in memory
    if isinstance(image, InMemoryUploadedFile):
        memory_image = BytesIO(image.read())
        pil_image = PilImage.open(memory_image)
        #img_format = os.path.splitext(image.name)[1][1:].upper()
        #img_format = 'JPEG' if img_format == 'JPG' else img_format

        if pil_image.width > max_width or pil_image.height > max_height:
            pil_image.thumbnail(size)

        # Convert to RGB because we will save the image as JPG
        pil_image = pil_image.convert('RGB')
        new_image = BytesIO()
        #pil_image.save(new_image, format=img_format)
        pil_image.save(new_image, format="JPEG")

        new_image = ContentFile(new_image.getvalue())
        return InMemoryUploadedFile(new_image, None, image.name, image.content_type, None, None)

    # Uploaded file is in disk
    elif isinstance(image, TemporaryUploadedFile):
        path = image.temporary_file_path()
        pil_image = PilImage.open(path)

        if pil_image.width > max_width or pil_image.height > max_height:
            pil_image.thumbnail(size)
            #pil_image.save(path)
            image.size = os.stat(path).st_size

    return image


@login_required
def upload_profile_pic(request):
    if request.method == "POST":
        form = UploadProfilePicForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data.get("file")
            # Resize
            #width, height = get_image_dimensions(image)
            max_width = max_height = 250
            image = resize_uploaded_image(image, max_width, max_height)

            # Save image
            file_name = str(request.user.id) + "-" + str(int(datetime.datetime.now().timestamp())) + ".jpg"
            full_path = "media/" + file_name
            with open(full_path, "wb+") as myfile:
                for chunk in image.chunks():
                    myfile.write(chunk)

            if UserProfile.objects.filter(user=request.user).exists():
                user_profile = UserProfile.objects.get(user=request.user)
                user_profile.profile_pic = file_name
                user_profile.save()
            else:
                user_profile = UserProfile.objects.create(
                    user=request.user,
                    profile_pic=image
                )
            return redirect("index")
        else:
            #print(form)
            messages.add_message(request, messages.ERROR, "Error")
    return redirect("index")
    


def delete(request):
    if request.method == "POST":
        if request.user.is_superuser:
            # Delete context
            Context.objects.all().delete()

            # Delete chat messages
            ChatHistory.objects.all().delete()

            # Delete chats
            Chat.objects.all().delete()

            # Delete invitation tokens
            InvitationToken.objects.all().delete()

            # Delete questions
            Question.objects.all().delete()

            # Delete conflict Infos
            ConflictInfo.objects.all().delete()

            # Delete users (except admins)
            User.objects.filter(is_superuser=False).delete()

            messages.add_message(request, messages.INFO, "Done, all clear")
        else:
            messages.add_message(request, messages.ERROR, "Only administrators can restart the application")

    return redirect("index")


