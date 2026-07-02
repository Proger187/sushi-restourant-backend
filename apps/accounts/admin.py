from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Customer, Favourite


@admin.register(Customer)
class CustomerAdmin(UserAdmin):
    model = Customer
    list_display = ["email", "first_name", "last_name", "is_staff", "is_active", "date_joined"]
    list_filter = ["is_staff", "is_active"]
    ordering = ["-date_joined"]
    search_fields = ["email", "first_name", "last_name"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "first_name", "last_name", "is_staff"),
        }),
    )


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ["customer", "product", "added_at"]
    raw_id_fields = ["customer", "product"]
