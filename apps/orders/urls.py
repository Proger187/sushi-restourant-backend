from django.urls import path

from . import views

urlpatterns = [
    path("orders/", views.OrderCreateView.as_view()),
    path("orders/<uuid:id>/", views.OrderDetailView.as_view()),
    path("admin/orders/", views.AdminOrderListView.as_view()),
    path("admin/orders/<uuid:id>/", views.AdminOrderDetailView.as_view()),
    path("admin/orders/<uuid:id>/status/", views.AdminOrderStatusUpdateView.as_view()),
]
