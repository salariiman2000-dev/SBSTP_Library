from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "phone_number",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "is_staff",
        "is_active",
        "is_superuser",
    )

    search_fields = (
        "username",
        "phone_number",
        "first_name",
        "last_name",
    )

    ordering = (
        "username",
    )

    fieldsets = (
        (
            "اطلاعات ورود",
            {
                "fields": (
                    "username",
                    "password",
                )
            },
        ),

        (
            "اطلاعات شخصی",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                    "profile_image",
                )
            },
        ),

        (
            "دسترسی‌ها",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),

        (
            "تاریخ‌های مهم",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            "ساخت کاربر",
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "phone_number",
                    "password1",
                    "password2",
                ),
            },
        ),
    )