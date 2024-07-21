from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login_view"),
    path("logout", views.logout_view, name="logout_view"),
    path("password-reset", views.password_reset_view, name="password-reset"),
    path("send-invitation", views.send_invitation, name="send-invitation"),
    path("signup", views.signup_code, name="signup-code"),
    path("signup/<str:value>", views.signup, name="signup"),
    path("change-profile-settings", views.change_profile_settings, name="change-profile-settings"),
    path("change-password", views.change_password, name="change-password"),
    path("backup", views.backup, name="backup"),
    path("restore", views.restore, name="restore"),
    path("upload-profile-pic", views.upload_profile_pic, name="upload-profile-pic"),
    path("delete", views.delete, name="delete"),
    path("create-chat", views.create_chat, name="create-chat"),
    path("chat/<str:uuid>/", views.chat, name="chat"),
    path("chat/<str:uuid>/update-chat-members", views.update_chat_members, name="update-chat-members"),
    path("chat/<str:uuid>/edit-chat", views.edit_chat, name="edit-chat"),
    path("chat/<str:uuid>/delete-chat", views.delete_chat, name="delete-chat"),
    path("chat/<str:uuid>/empty-chat", views.empty_chat, name="empty-chat"),
    path("chat/<str:uuid>/leave-chat", views.leave_chat, name="leave-chat"),
    path("chat/<str:uuid>/request-mediation", views.request_mediation, name="request-mediation"),
    path("chat/<str:uuid>/generate-user-answer", views.generate_user_answer, name="generate-user-answer"),
    path("conflict-info", views.conflict_info, name="conflict-info"),
]