from django.conf import settings
from django.db import models


class ActivityLog(models.Model):

    ACTION_LOGIN = "login"
    ACTION_LOGOUT = "logout"
    ACTION_CREATE = "create"
    ACTION_UPDATE = "update"
    ACTION_DELETE = "delete"
    ACTION_LOAN = "loan"
    ACTION_RETURN = "return"
    ACTION_STATUS = "status"
    ACTION_ROLE = "role"
    ACTION_OTHER = "other"

    ACTION_CHOICES = [
        (ACTION_LOGIN, "ورود"),
        (ACTION_LOGOUT, "خروج"),
        (ACTION_CREATE, "افزودن"),
        (ACTION_UPDATE, "ویرایش"),
        (ACTION_DELETE, "حذف"),
        (ACTION_LOAN, "امانت"),
        (ACTION_RETURN, "برگشت امانت"),
        (ACTION_STATUS, "تغییر وضعیت"),
        (ACTION_ROLE, "تغییر نقش"),
        (ACTION_OTHER, "سایر"),
    ]

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_logs",
        verbose_name="انجام‌دهنده",
    )

    action = models.CharField(
        "نوع عملیات",
        max_length=20,
        choices=ACTION_CHOICES,
    )

    section = models.CharField(
        "بخش",
        max_length=100,
        blank=True,
    )

    description = models.TextField(
        "توضیحات",
    )

    object_id = models.CharField(
        "شناسه رکورد",
        max_length=100,
        blank=True,
    )

    ip_address = models.GenericIPAddressField(
        "آدرس IP",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        "تاریخ و ساعت",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "رویداد"
        verbose_name_plural = "رویدادها"
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return (
            f"{self.get_action_display()} - "
            f"{self.description}"
        )