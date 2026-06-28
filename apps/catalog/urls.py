from django.urls import path

from . import views

urlpatterns = [
    path("categories/", views.CategoryListView.as_view()),
    path("products/", views.ProductListView.as_view()),
    path("products/<slug:slug>/", views.ProductDetailView.as_view()),
    path("admin/categories/", views.AdminCategoryListCreateView.as_view()),
    path("admin/categories/<slug:slug>/", views.AdminCategoryUpdateDeleteView.as_view()),
    path("admin/products/", views.AdminProductListCreateView.as_view()),
    path("admin/products/<slug:slug>/", views.AdminProductUpdateDeleteView.as_view()),
]
