from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def permission_required(permission):
    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if not request.user.is_authenticated:
                return redirect("dashboard_login")

            if not request.user.is_staff:
                messages.error(
                    request,
                    "شما اجازه دسترسی به پنل مدیریت را ندارید."
                )
                return redirect("home")

            if request.user.is_superuser:
                return view_func(
                    request,
                    *args,
                    **kwargs,
                )

            if not request.user.has_perm(permission):
                messages.error(
                    request,
                    "شما اجازه دسترسی به این بخش را ندارید."
                )

                return redirect("dashboard_home")

            return view_func(
                request,
                *args,
                **kwargs,
            )

        return wrapper

    return decorator