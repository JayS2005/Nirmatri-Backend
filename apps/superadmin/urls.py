from django.urls import path
from .views import superadmin_login, get_pending_sellers, approve_seller, all_sellers, reject_seller, admin_dashboard, recent_activities

urlpatterns = [
    path("login/", superadmin_login),
    path("pending-sellers/", get_pending_sellers),
    path("seller/approve/<str:seller_id>/", approve_seller),
    path("sellers/", all_sellers),
    path("seller/reject/<str:seller_id>/", reject_seller),
    path("dashboard/", admin_dashboard),
      path("activities/", recent_activities),
]
