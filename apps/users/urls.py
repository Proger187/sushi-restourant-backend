from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    path("auth/customer/register/", views.CustomerRegisterView.as_view()),
    path("auth/customer/token/", TokenObtainPairView.as_view()),
    path("auth/customer/token/refresh/", TokenRefreshView.as_view()),
    path("auth/customer/profile/", views.CustomerProfileView.as_view()),
]
