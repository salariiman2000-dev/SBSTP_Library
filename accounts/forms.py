from django import forms
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm,
)

User = get_user_model()


def normalize_digits(value):
    """تبدیل اعداد فارسی و عربی به انگلیسی."""

    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    english_digits = "0123456789"

    translation_table = str.maketrans(
        persian_digits + arabic_digits,
        english_digits + english_digits,
    )

    return value.translate(translation_table)


class PhoneRegisterForm(forms.Form):

    phone_number = forms.CharField(
        label="شماره موبایل",
        max_length=11,
        min_length=11,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "09123456789",
                "inputmode": "numeric",
                "autocomplete": "tel",
                "dir": "ltr",
            }
        ),
        error_messages={
            "required": "لطفاً شماره موبایل خود را وارد کنید.",
            "max_length": "شماره موبایل باید ۱۱ رقم باشد.",
            "min_length": "شماره موبایل باید ۱۱ رقم باشد.",
        },
    )

    def clean_phone_number(self):
        phone = self.cleaned_data["phone_number"]

        phone = normalize_digits(phone)

        phone = (
            phone
            .replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
        )

        # تبدیل شماره‌های +98 و 98 به فرمت 09
        if phone.startswith("+98"):
            phone = "0" + phone[3:]

        elif phone.startswith("98"):
            phone = "0" + phone[2:]

        if not phone.startswith("09"):
            raise forms.ValidationError(
                "شماره موبایل باید با 09 شروع شود."
            )

        if len(phone) != 11:
            raise forms.ValidationError(
                "شماره موبایل باید ۱۱ رقم باشد."
            )

        if not phone.isdigit():
            raise forms.ValidationError(
                "شماره موبایل فقط باید شامل عدد باشد."
            )

        if User.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError(
                "این شماره موبایل قبلاً استفاده شده است."
            )

        return phone





class OTPForm(forms.Form):

    otp = forms.CharField(
        label="کد تأیید",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "کد ۶ رقمی",
                "inputmode": "numeric",
                "autocomplete": "one-time-code",
                "dir": "ltr",
                "maxlength": "6",
            }
        ),
        error_messages={
            "required": "لطفاً کد تأیید را وارد کنید.",
            "max_length": "کد تأیید باید ۶ رقم باشد.",
            "min_length": "کد تأیید باید ۶ رقم باشد.",
        },
    )

    def clean_otp(self):

        otp = normalize_digits(
            self.cleaned_data["otp"]
        ).strip()

        if not otp.isdigit():
            raise forms.ValidationError(
                "کد تأیید فقط باید شامل عدد باشد."
            )

        if len(otp) != 6:
            raise forms.ValidationError(
                "کد تأیید باید ۶ رقم باشد."
            )

        return otp




class RegisterForm(UserCreationForm):

    first_name = forms.CharField(
        label="نام",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "نام",
                "autocomplete": "given-name",
            }
        ),
        error_messages={
            "required": "لطفاً نام خود را وارد کنید.",
        },
    )

    last_name = forms.CharField(
        label="نام خانوادگی",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "نام خانوادگی",
                "autocomplete": "family-name",
            }
        ),
        error_messages={
            "required": "لطفاً نام خانوادگی خود را وارد کنید.",
        },
    )

    username = forms.CharField(
        label="نام کاربری",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "نام کاربری",
                "autocomplete": "username",
                "dir": "ltr",
            }
        ),
        error_messages={
            "required": "لطفاً نام کاربری را وارد کنید.",
        },
    )

    password1 = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "رمز عبور",
                "autocomplete": "new-password",
                "dir": "ltr",
            }
        ),
        error_messages={
            "required": "لطفاً رمز عبور را وارد کنید.",
        },
    )

    password2 = forms.CharField(
        label="تکرار رمز عبور",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "تکرار رمز عبور",
                "autocomplete": "new-password",
                "dir": "ltr",
            }
        ),
        error_messages={
            "required": "لطفاً تکرار رمز عبور را وارد کنید.",
        },
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "password1",
            "password2",
        )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "این نام کاربری قبلاً استفاده شده است."
            )

        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                "رمز عبور و تکرار آن یکسان نیستند."
            )

        return password2


class LoginForm(AuthenticationForm):

    username = forms.CharField(
        label="نام کاربری",
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "نام کاربری",
                "autocomplete": "username",
                "dir": "ltr",
            }
        ),
        error_messages={
            "required": "لطفاً نام کاربری را وارد کنید.",
        },
    )

    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "رمز عبور",
                "autocomplete": "current-password",
                "dir": "ltr",
            }
        ),
        error_messages={
            "required": "لطفاً رمز عبور را وارد کنید.",
        },
    )

    error_messages = {
        "invalid_login": "نام کاربری یا رمز عبور اشتباه است.",
        "inactive": "این حساب کاربری غیرفعال است.",
    }


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User

        # ایمیل و شماره موبایل عمداً اینجا نیستند.
        fields = (
            "first_name",
            "last_name",
            "profile_image",
        )

        labels = {
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "profile_image": "تصویر پروفایل",
        }

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "نام",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "نام خانوادگی",
                }
            ),

            "profile_image": forms.ClearableFileInput(
                attrs={
                    "class": "form-input",
                }
            ),
        }


class CustomPasswordChangeForm(PasswordChangeForm):

    old_password = forms.CharField(
        label="رمز عبور فعلی",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "رمز عبور فعلی",
                "autocomplete": "current-password",
                "dir": "ltr",
            }
        ),
        error_messages={
            "required": "لطفاً رمز عبور فعلی را وارد کنید.",
        },
    )

    new_password1 = forms.CharField(
        label="رمز عبور جدید",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "رمز عبور جدید",
                "autocomplete": "new-password",
                "dir": "ltr",
            }
        ),
        error_messages={
            "required": "لطفاً رمز عبور جدید را وارد کنید.",
        },
    )

    new_password2 = forms.CharField(
        label="تکرار رمز عبور جدید",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "تکرار رمز عبور جدید",
                "autocomplete": "new-password",
                "dir": "ltr",
            }
        ),
        error_messages={
            "required": "لطفاً تکرار رمز عبور جدید را وارد کنید.",
        },
    )

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")

        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                "رمز عبور فعلی اشتباه است."
            )

        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                "رمز عبور جدید و تکرار آن یکسان نیستند."
            )

        return password2