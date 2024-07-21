from django import forms


class LoginForm(forms.Form):
    #username = forms.EmailField(label="Email", max_length=100, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Email"}))
    username = forms.CharField(label="Email", max_length=100, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Email", "autocomplete": "off"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control", "placeholder":"Password"}))


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=100, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Email", "id":"password_reset_form_email_id"}))


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control", "placeholder":"Current password"}))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control", "placeholder":"New password"}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control", "placeholder":"Confirm password"}))


class InvitationForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=100, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Email", "autocomplete": "off", "id":"invitation_form_email_id"}))
    #message = forms.CharField(label="Description", max_length=1000, widget=forms.Textarea(attrs={"class":"form-control", "rows":5, "data-autosize":"true", "style":"min-height: 100px;"}), required=False)

class SignupForm(forms.Form):
    username = forms.CharField(label="Username", max_length=100, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Username", "autocomplete": "off"}))
    first_name = forms.CharField(label="First name", max_length=100, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"First Name", "autocomplete": "off"}))
    last_name = forms.CharField(label="Last name", max_length=100, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Last Name", "autocomplete": "off"}))
    email = forms.EmailField(label="Email", max_length=100, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Email", "autocomplete": "off", "id":"signup_form_email_id"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control", "placeholder":"Password"}))
    token = forms.CharField(widget = forms.HiddenInput())

class SignupCodeForm(forms.Form):
    username = forms.CharField(label="Username", max_length=100, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Username", "autocomplete": "off"}))
    first_name = forms.CharField(label="First name", max_length=100, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"First Name", "autocomplete": "off"}))
    last_name = forms.CharField(label="Last name", max_length=100, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Last Name", "autocomplete": "off"}))
    email = forms.EmailField(label="Email", max_length=100, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Email", "autocomplete": "off", "id":"signup_form_email_id"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control", "placeholder":"Password"}))
    code = forms.CharField(label="Code", max_length=100, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Code", "autocomplete": "off"}))


class ProfileSettingsForm(forms.Form):
    username = forms.CharField(label="Username", max_length=100, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Username", "autocomplete": "off"}))
    first_name = forms.CharField(label="First name", max_length=100, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"First Name", "autocomplete": "off"}))
    last_name = forms.CharField(label="Last name", max_length=100, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Last Name", "autocomplete": "off"}))
    email = forms.EmailField(label="Email", max_length=100, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Email", "autocomplete": "off", "id":"profile_settings_form_email_id"}))
    is_party = forms.BooleanField(label="Party to conflict", widget=forms.CheckboxInput(attrs={"class":"form-check-input"}), required=False)

class UploadBackupFileForm(forms.Form):
    backup_file = forms.FileField(widget=forms.FileInput(attrs={"class":"form-control"}))


class UploadProfilePicForm(forms.Form):
    file = forms.ImageField()
    #file = forms.FileField()

class ConflictInfoForm(forms.Form):
    #subject = forms.CharField(label="Subject", max_length=100, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Subject","autocomplete": "off",}))
    attrs={
        "class":"form-control", 
        "rows":5, 
        "data-autosize":"true",
        "autocomplete": "off", 
        "style":"overflow-y: scroll; min-height: 110px;",
        "id":"conflict_info_form_description_id",
        }
    description = forms.CharField(label="Description", max_length=10000, widget=forms.Textarea(attrs=attrs), required=False)


class CreateChatForm(forms.Form):
    name = forms.CharField(label="Name", max_length=100, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Chat name","autocomplete": "off", "id":"create_chat_form_name_id"}))
    attrs={
        "class":"form-control", 
        "rows":8, 
        "data-autosize":"true",
        "autocomplete": "off", 
        "style":"min-height: 100px;",
        "id":"create_chat_form_description_id",
        }
    description = forms.CharField(label="Description", max_length=1000, required=False, widget=forms.Textarea(attrs=attrs))
    members = forms.MultipleChoiceField(widget  = forms.CheckboxSelectMultiple, required=False)

class EditChatForm(forms.Form):
    name = forms.CharField(label="Name", max_length=100, widget=forms.TextInput(attrs={"class":"form-control", "placeholder":"Chat name","autocomplete": "off", "id":"edit_chat_form_name_id"}))
    attrs={
        "class":"form-control", 
        "rows":8, 
        "data-autosize":"true",
        "autocomplete": "off", 
        "style":"min-height: 100px;",
        "id":"edit_chat_form_description_id",
        }
    description = forms.CharField(label="Description", max_length=1000, required=False, widget=forms.Textarea(attrs=attrs))


class UpdateChatMembersForm(forms.Form):
    members = forms.MultipleChoiceField(widget  = forms.CheckboxSelectMultiple, required=False)


class ChatForm(forms.Form):
    attrs = {
        "autocomplete": "off",
        "class":"form-control px-0", 
        "placeholder":"Type your message...",
        "rows":1,
        "data-emoji-input":"",
        "data-autosize":"true"
        }
    chat_message = forms.CharField(label="Chat message", max_length=1000, widget=forms.TextInput(attrs=attrs))
    """
    uploaded_file = forms.FileField(
		required=False,
		widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
	)
    """
