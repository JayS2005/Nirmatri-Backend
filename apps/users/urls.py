from django.urls import path
from .views import user_login, get_profile, update_profile, logout_user, user_register

urlpatterns = [
    path("profile/", get_profile),
    path("register/", user_register),
    path("login/", user_login),
    path("logOut/", logout_user),
    path("profile/update/", update_profile),
    
]
