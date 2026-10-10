from django.urls import path

from . import views


app_name = "accounts"


urlpatterns = [

    path(
        "register/",
        views.register_phone_view,
        name="register_phone",
    ),

    path(
        "register/details/",
        views.register_details_view,
        name="register_details",
    ),

    path(
        "login/",
        views.login_view,
        name="login",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

    path(
        "profile/",
        views.profile_view,
        name="profile",
    ),

    path(
        "profile/edit/",
        views.edit_profile_view,
        name="edit_profile",
    ),

    path(
        "password/change/",
        views.ChangePasswordView.as_view(),
        name="change_password",
    ),
    path(
        "register/verify/",
        views.verify_otp_view,
        name="verify_otp",
    ),


]