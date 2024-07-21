from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from app.forms import LoginForm, PasswordResetForm, InvitationForm, SignupForm, SignupCodeForm
from app.models import InvitationToken

from hashids import Hashids
import random
import string


def generate_token():
    return ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=64))


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            username = username.lower()
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("index")
            else:
                messages.add_message(request, messages.ERROR, "You have entered an invalid username or password")
                return redirect("login_view")
    else:
        form = LoginForm()
    
    return render(request, "login.html", {"form":form})


def logout_view(request):
    logout(request)
    return redirect("index")


def password_reset_view(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            return redirect("login_view")
    else:
        form = PasswordResetForm()

    return render(request, "password-reset.html", {"form":form})


@require_POST
@login_required
def send_invitation(request):
    form = InvitationForm(request.POST)
    if form.is_valid():
        invitation_from = request.user
        invitation_to = form.cleaned_data["email"]
        #message = form.cleaned_data["message"]
        token = generate_token()

        InvitationToken.objects.create(
            invitation_from = invitation_from,
            invitation_to = invitation_to,
            #message = message,
            token = token,
        )
        invitation_link = request.build_absolute_uri("/signup/" + token)

        body = f"{invitation_link}"
        
        res = send_mail(
            "Invitation",
            body,
            settings.EMAIL_HOST_USER,
            [invitation_to],
            fail_silently=False,
        )

        messages.add_message(request, messages.INFO, "Invitation sent")
    else:
        messages.add_message(request, messages.ERROR, "Please enter a valid email")
        
    return redirect("index")



def signup(request, value):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            email = email.lower()
            password = form.cleaned_data["password"]
            token = form.cleaned_data["token"]

            # Check if token exists and corresponds to email
            if InvitationToken.objects.filter(invitation_to=email, token=token).exists():
                InvitationToken.objects.filter(invitation_to=email, token=token).delete()
                # Check if username exists
                if not User.objects.filter(email=email).exists():
                    User.objects.create_user(
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=password)
                else:
                    print("Email already in use")
            else:
                print("Wrong token")
            
            return redirect("index")
            
    else:
        initial = {"token":value}
        form = SignupForm(initial=initial)
    
    return render(request, "signup.html", {"form":form})


def signup_code(request):
    if request.method == "POST":
        form = SignupCodeForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            email = email.lower()
            password = form.cleaned_data["password"]
            code = form.cleaned_data["code"]
            
            # Check if code is valid
            hash_id = Hashids(salt=settings.SECRET_KEY, min_length=6, alphabet="abcdefghijklmnopqrstuvxyz0123456789")
            hash_decoded = hash_id.decrypt(code)
            if not hash_decoded:
                messages.add_message(request, messages.ERROR, "Code is not correct")
                return redirect("signup-code")
            else:
                # Check if email exists
                if not User.objects.filter(email=email).exists():

                    User.objects.create_user(
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=password)

                    messages.add_message(request, messages.INFO, "User created")
                    return redirect("index")
                    
                else:
                    messages.add_message(request, messages.ERROR, "Error, email already in use")
                    return redirect("signup-code")
            
        messages.add_message(request, messages.ERROR, "Error")
    else:
        form = SignupCodeForm()
    
    return render(request, "signup-code.html", {"form":form})
