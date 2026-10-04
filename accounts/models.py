from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = None

    phone_number = models.CharField(
        "شماره موبایل",
        max_length=11,
        unique=True,
        blank=False,
        null=False,
    )

    profile_image = models.ImageField(
        "تصویر پروفایل",
        upload_to="profiles/",
        null=True,
        blank=True,
    )

    class Meta:
        permissions = [
            (
                "access_dashboard",
                "دسترسی به پنل مدیریت",
            ),
            (
                "manage_roles",
                "مدیریت نقش‌های کاربران",
            ),
        ]

    def __str__(self):
        return self.username