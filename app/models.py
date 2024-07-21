from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_profile")
    profile_pic = models.ImageField(upload_to="media/profile_pics/", default="default.jpg")
    is_party = models.BooleanField(default=True)
    initial_interview_concluded = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
    def username(self):
        return self.user.username
    
    def email(self):
        return self.user.email
    
    def first_name(self):
        return self.user.first_name
    
    def last_name(self):
        return self.user.last_name
    

class ConflictInfo(models.Model):
    #subject = models.CharField(max_length=255, db_index = True)
    description = models.TextField(blank=True, null=True, default="")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by")
    created_at = models.DateTimeField(auto_now_add=True)

class Question(models.Model):
    question = models.TextField(blank=True, null=True, default="")
    answer = models.TextField(blank=True, null=True, default="")
    question_for = models.ForeignKey(User, on_delete=models.CASCADE, related_name="question_for")


class InvitationToken(models.Model):
    id = models.AutoField(primary_key=True)
    invitation_from = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=0, related_name="invitations")
    invitation_to = models.CharField(max_length=255)
    message = models.TextField(blank=True, null=True, default="")
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class Chat(models.Model):
    uuid = models.CharField(max_length=255, primary_key=True)
    permalink = models.CharField(max_length=255)
    name = models.CharField(max_length=255, db_index = True)
    description = models.TextField(blank=True, null=True, default="")
    members = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    is_caucus = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    
class ChatHistory(models.Model):
    id = models.AutoField(primary_key=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sent_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    is_llm = models.BooleanField(default=False)
    is_relevant = models.BooleanField(default=True)
    message = models.TextField(blank=True, null=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.message


class Context(models.Model):
    id = models.AutoField(primary_key=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    context_type = models.CharField(max_length=255, default="")
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


