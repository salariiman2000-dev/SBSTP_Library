from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver


SYSTEM_MANAGER = "مدیر سیستم"
CONTENT_MANAGER = "مدیر محتوا"
USER_MANAGER = "مدیر کاربران"


@receiver(post_migrate)
def create_library_roles(sender, **kwargs):

    required_permissions = {
        "access_dashboard": (
            "accounts",
            "access_dashboard",
        ),
        "manage_roles": (
            "accounts",
            "manage_roles",
        ),
        "view_user": (
            "accounts",
            "view_user",
        ),
        "add_user": (
            "accounts",
            "add_user",
        ),
        "change_user": (
            "accounts",
            "change_user",
        ),
        "delete_user": (
            "accounts",
            "delete_user",
        ),
        "manage_books": (
            "blog",
            "manage_books",
        ),
        "manage_categories": (
            "blog",
            "manage_categories",
        ),
        "manage_loans": (
            "blog",
            "manage_loans",
        ),
    }

    permissions = {}

    for name, (app_label, codename) in required_permissions.items():

        permission = Permission.objects.filter(
            content_type__app_label=app_label,
            codename=codename,
        ).first()

        if permission is None:
            # هنوز تمام Permissionها ساخته نشده‌اند.
            # post_migrate برای appهای بعدی دوباره اجرا می‌شود.
            return

        permissions[name] = permission


    # =========================
    # Groups
    # =========================

    system_manager, _ = Group.objects.get_or_create(
        name=SYSTEM_MANAGER
    )

    content_manager, _ = Group.objects.get_or_create(
        name=CONTENT_MANAGER
    )

    user_manager, _ = Group.objects.get_or_create(
        name=USER_MANAGER
    )


    # =========================
    # System Manager
    # =========================

    system_manager.permissions.set(
        Permission.objects.all()
    )


    # =========================
    # Content Manager
    # =========================

    content_manager.permissions.set([
        permissions["access_dashboard"],
        permissions["manage_books"],
        permissions["manage_categories"],
        permissions["manage_loans"],
    ])


    # =========================
    # User Manager
    # =========================

    user_manager.permissions.set([
        permissions["access_dashboard"],
        permissions["view_user"],
        permissions["add_user"],
        permissions["change_user"],
        permissions["delete_user"],
    ])


    # =========================
    # System Manager Role Management
    # =========================

    system_manager.permissions.add(
        permissions["manage_roles"]
    )