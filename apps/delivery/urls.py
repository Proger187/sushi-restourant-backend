from django.urls import path

from . import views

urlpatterns = [
    path("delivery/calculate/", views.DeliveryCalculateView.as_view()),
    path("admin/delivery-zones/", views.AdminDeliveryZoneListCreateView.as_view()),
    path("admin/delivery-zones/<uuid:pk>/", views.AdminDeliveryZoneUpdateDeleteView.as_view()),
]
