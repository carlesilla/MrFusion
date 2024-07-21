from django.contrib import admin
from app.models import UserProfile
from django.contrib.auth.models import User


# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "first_name", "last_name", "profile_pic"]

