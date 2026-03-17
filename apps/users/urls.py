from django.urls import path
from .views import user_login, get_profile, update_profile, logout_user, user_register, add_address, get_addresses, delete_address, set_default_address


urlpatterns = [
    path("profile/", get_profile),
    path("register/", user_register),
    path("login/", user_login),
    path("logOut/", logout_user),
    path("profile/update/", update_profile),
    path("address/", add_address),
    path("addresses/", get_addresses),
    path("address/<str:address_id>/", delete_address),
    path("address/default/", set_default_address),
    
]
