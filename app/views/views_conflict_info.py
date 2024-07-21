from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.http import HttpResponse
from django.shortcuts import render, redirect

from app import mediator
from app.forms import ConflictInfoForm
from app.models import ConflictInfo
from app.views import views_utils


@login_required
def conflict_info(request):
    context = views_utils.get_context(request)
    context["section"] = "conflict_info"
    if request.method == "POST":
        form = ConflictInfoForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data["description"]
            # Delete previous
            if ConflictInfo.objects.filter(created_by=request.user).exists():
                ConflictInfo.objects.filter(created_by=request.user).delete()
            
            info = ConflictInfo.objects.create(
                description = description,
                created_by = request.user
            )
            messages.add_message(request, messages.INFO, "Conflict information updated successfully")
        else:
            messages.add_message(request, messages.ERROR, "An error has occurred, please check the fields and try again.")

        return redirect("index")
    
    if ConflictInfo.objects.filter(created_by=request.user).exists():
        info = ConflictInfo.objects.filter(created_by=request.user).order_by("created_at").last()
        context["info"] = info
        initial = {"description":info.description}
        
    else:
        initial = {}
    
    form = ConflictInfoForm(initial)
    context["conflict_info_form"] = form

    return render(request, "conflict-info.html", context = context)
