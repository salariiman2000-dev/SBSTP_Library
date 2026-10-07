from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    email = None

    phone_number = models.CharField(
        "شماره موبایل",
        max_length=11,
        unique=True,
        blank=True,
        null=True,
    )

    father_name = models.CharField(
        "نام پدر",
        max_length=150,
        blank=True,
        null=True,
    )

    national_code = models.CharField(
        "کد ملی",
        max_length=10,
        unique=True,
        blank=True,
        null=True,
    )

    birth_date = models.DateField(
        "تاریخ تولد",
        blank=True,
        null=True,
    )

    home_address = models.TextField(
        "آدرس منزل",
        blank=True,
        null=True,
    )

    profile_image = models.ImageField(
        "تصویر پروفایل",
        upload_to="profiles/",
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["phone_number"]

    objects = UserManager()

    class Meta:
        permissions = [
            ("access_dashboard", "دسترسی به پنل مدیریت"),
            ("manage_roles", "مدیریت نقش‌های کاربران"),
        ]

    def __str__(self):
        return self.username