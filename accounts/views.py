import random
import time
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from blog.models import Loan, Favorite
from .forms import *



def register_phone_view(request):

    if request.user.is_authenticated:
        return redirect("accounts:profile")

    if request.method == "POST":

        form = PhoneRegisterForm(request.POST)

        if form.is_valid():

            phone = form.cleaned_data["phone_number"]

            # تولید کد ۶ رقمی آزمایشی
            otp = str(random.randint(100000, 999999))

            # ذخیره در session
            request.session["register_phone"] = phone
            request.session["register_otp"] = otp

            # شماره هنوز تأیید نشده
            request.session["register_phone_verified"] = False

            return redirect(
                "accounts:verify_otp"
            )

    else:

        form = PhoneRegisterForm()

    return render(
        request,
        "accounts/register_phone.html",
        {
            "form": form
        }
    )


def register_details_view(request):

    if request.user.is_authenticated:
        return redirect("accounts:profile")

    phone = request.session.get(
        "register_phone"
    )

    phone_verified = request.session.get(
        "register_phone_verified"
    )

    if not phone or not phone_verified:

        return redirect(
            "accounts:register_phone"
        )

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save(
                commit=False
            )

            user.phone_number = phone

            user.save()

            request.session.pop(
                "register_phone",
                None
            )

            request.session.pop(
                "register_phone_verified",
                None
            )

            login(
                request,
                user
            )

            messages.success(
                request,
                "حساب کاربری شما با موفقیت ایجاد شد."
            )

            return redirect(
                "accounts:profile"
            )

    else:

        form = RegisterForm()

    return render(
        request,
        "accounts/register_details.html",
        {
            "form": form,
            "phone": phone,
        }
    )


def login_view(request):

    if request.user.is_authenticated:
        return redirect("accounts:profile")

    next_url = request.GET.get("next")

    if request.method == "POST":
        form = LoginForm(
            request=request,
            data=request.POST,
        )

        if form.is_valid():
            user = form.get_user()

            login(request, user)

            return redirect(
                request.POST.get("next")
                or next_url
                or "accounts:profile"
            )

    else:
        form = LoginForm()

    return render(
        request,
        "accounts/login.html",
        {
            "form": form,
            "next": next_url,
        },
    )


@login_required
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "با موفقیت از حساب کاربری خارج شدید.",
    )

    return redirect("/")


@login_required
def profile_view(request):

    # اعلان علاقه‌مندی خوانده شد
    request.session.pop("favorite_notification", None)

    loans = (
        Loan.objects
        .filter(user=request.user)
        .select_related("book", "book__category")
    )

    active_loans = loans.filter(
        status=Loan.STATUS_BORROWED
    )

    pending_loans = loans.filter(
        status=Loan.STATUS_PENDING
    )

    returned_loans = loans.filter(
        status=Loan.STATUS_RETURNED
    )

    # کتاب‌های ذخیره‌شده / علاقه‌مندی‌ها
    favorites = (
        Favorite.objects
        .filter(user=request.user)
        .select_related("book", "book__category")
        .order_by("-created_at")
    )

    return render(
        request,
        "accounts/profile.html",
        {
            "user": request.user,
            "loans": loans,
            "active_loans": active_loans,
            "pending_loans": pending_loans,
            "returned_loans": returned_loans,
            "favorites": favorites,
        },
    )


@login_required
def edit_profile_view(request):

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "اطلاعات پروفایل با موفقیت ذخیره شد.",
            )

            return redirect("accounts:profile")

    else:
        form = ProfileForm(
            instance=request.user,
        )

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "form": form,
        },
    )


class ChangePasswordView(PasswordChangeView):

    form_class = CustomPasswordChangeForm

    template_name = "accounts/change_password.html"

    success_url = reverse_lazy(
        "accounts:profile"
    )

    def form_valid(self, form):
        messages.success(
            self.request,
            "رمز عبور شما با موفقیت تغییر کرد.",
        )

        return super().form_valid(form)
    







def verify_otp_view(request):

    if request.user.is_authenticated:
        return redirect("accounts:profile")

    phone = request.session.get(
        "register_phone"
    )

    saved_otp = request.session.get(
        "register_otp"
    )

    if not phone or not saved_otp:

        return redirect(
            "accounts:register_phone"
        )

    if request.method == "POST":

        form = OTPForm(request.POST)

        if form.is_valid():

            entered_otp = form.cleaned_data["otp"]

            if entered_otp != saved_otp:

                form.add_error(
                    "otp",
                    "کد وارد شده اشتباه است."
                )

            else:

                request.session[
                    "register_phone_verified"
                ] = True

                request.session.pop(
                    "register_otp",
                    None
                )

                messages.success(
                    request,
                    "شماره موبایل با موفقیت تأیید شد."
                )

                return redirect(
                    "accounts:register_details"
                )

    else:

        form = OTPForm()

    return render(
        request,
        "accounts/verify_otp.html",
        {
            "form": form,
            "phone": phone,
            "test_otp": saved_otp,
        }
    )