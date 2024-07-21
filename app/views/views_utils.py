from django.conf import settings
from django.contrib.auth.models import User
from django.utils.text import slugify

from app.forms import InvitationForm, UploadProfilePicForm, CreateChatForm, ChatForm, ProfileSettingsForm, ChangePasswordForm, UploadBackupFileForm
from app.models import UserProfile, Chat, ChatHistory

from hashids import Hashids
import uuid as uuid_generator



def get_context(request):
    # User profile
    if UserProfile.objects.filter(user=request.user).exists():
        user_profile = UserProfile.objects.get(user=request.user)
    else:
        user_profile = UserProfile.objects.create(user=request.user)

    # Profile
    initial = {
        "username": request.user.username,
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "email": request.user.email,
        "is_party": request.user.user_profile.is_party,
    }
    profile_settings_form = ProfileSettingsForm(initial=initial)
    change_password_form = ChangePasswordForm()
    upload_profile_pic_form = UploadProfilePicForm()
    

    # Contacts
    contacts = User.objects.filter(is_active=True)

    # Invitation form
    invitation_form = InvitationForm()
    hash_id = Hashids(salt=settings.SECRET_KEY, min_length=6, alphabet="abcdefghijklmnopqrstuvxyz0123456789")
    invitation_code = hash_id.encrypt(request.user.id)

    # Create chat form
    create_chat_form = CreateChatForm()
    choices = []
    for contact in contacts:
        choices.append((contact.id, contact.id))
    create_chat_form.fields["members"].choices = choices    
    
    # Chats (only is user is_party)
    # All users have a One to One chat with MrFusion
    if request.user.user_profile.is_party == True:
        if not Chat.objects.filter(members=request.user, is_caucus=True).exists():
            uuid = str(uuid_generator.uuid4())
            name = request.user.first_name + " <> MrFusion" 
            permalink = slugify(name)
            description = "One-to-one chat with MrFusion"
            caucus_chat = Chat.objects.create(
                    uuid = uuid,
                    permalink = permalink,
                    name = name,
                    description = description,
                    owner = request.user,
                    is_caucus=True,
                )
            caucus_chat.members.add(request.user)

            #message = "Can you tell me what the problem is?"
            #ChatHistory.objects.create(chat=caucus_chat, message=message, is_llm=True)

    #chats = Chat.objects.filter(members=request.user).order_by('chathistory__created_at')
    if request.user.is_superuser:
        chats = Chat.objects.filter(is_caucus=False)
    else:
        chats = Chat.objects.filter(members=request.user).order_by("-is_caucus", "created_at")
    

    chat_form = ChatForm()

    context = {
        #"user": request.user,
        "user_profile":user_profile,
        "contacts": contacts,
        "profile_settings_form": profile_settings_form,
        "change_password_form": change_password_form,
        "invitation_form": invitation_form,
        "invitation_code": invitation_code,
        "upload_profile_pic_form":upload_profile_pic_form, 
        "create_chat_form": create_chat_form,
        "chats": chats,
        "chat_form": chat_form,
        }
    
    # If superuser:
    if request.user.is_superuser == True:
        upload_backup_file_form = UploadBackupFileForm()
        context["upload_backup_file_form"] = upload_backup_file_form
    
    return context
