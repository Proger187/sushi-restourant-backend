from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("accounts/register/", views.CustomerRegisterView.as_view()),
    path("accounts/login/", views.CustomerLoginView.as_view()),
    path("accounts/token/refresh/", TokenRefreshView.as_view()),
    path("accounts/profile/", views.CustomerProfileView.as_view()),
    path("accounts/orders/", views.CustomerOrderHistoryView.as_view()),
    path("accounts/favourites/", views.FavouriteListView.as_view()),
    path("accounts/favourites/<uuid:product_id>/", views.FavouriteDeleteView.as_view()),
    path("accounts/change-password/", views.CustomerChangePasswordView.as_view()),
]
