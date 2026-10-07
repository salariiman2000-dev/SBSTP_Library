from django import forms
from django.contrib.auth import (
    get_user_model,
)
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm,
)
from django.utils import timezone
import jdatetime


User = get_user_model()


def normalize_digits(value):
    """
    تبدیل اعداد فارسی و عربی به انگلیسی.
    """

    if value is None:
        return ""

    value = str(value)

    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    english_digits = "0123456789"

    translation_table = str.maketrans(
        persian_digits + arabic_digits,
        english_digits + english_digits,
    )

    return value.translate(translation_table)


def gregorian_to_jalali(value):
    """
    تبدیل تاریخ میلادی به شمسی.
    """

    if not value:
        return ""

    return jdatetime.date.fromgregorian(
        date=value
    ).strftime("%Y/%m/%d")


def jalali_to_gregorian(value):
    """
    تبدیل تاریخ شمسی به میلادی.
    """

    value = normalize_digits(value).strip()

    value = (
        value
        .replace("-", "/")
        .replace(".", "/")
    )

    parts = value.split("/")

    if len(parts) != 3:
        raise ValueError(
            "تاریخ باید به صورت YYYY/MM/DD باشد."
        )

    year = int(parts[0])
    month = int(parts[1])
    day = int(parts[2])

    if not 1 <= month <= 12:
        raise ValueError(
            "ماه تاریخ تولد نامعتبر است."
        )

    if not 1 <= day <= 31:
        raise ValueError(
            "روز تاریخ تولد نامعتبر است."
        )

    jalali_date = jdatetime.date(
        year,
        month,
        day,
    )

    return jalali_date.togregorian()


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

        if User.objects.filter(
            phone_number=phone
        ).exists():
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

    father_name = forms.CharField(
        label="نام پدر",
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "نام پدر",
            }
        ),
        error_messages={
            "required": "لطفاً نام پدر را وارد کنید.",
        },
    )

    national_code = forms.CharField(
        label="کد ملی",
        max_length=10,
        min_length=10,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "کد ملی ۱۰ رقمی",
                "inputmode": "numeric",
                "maxlength": "10",
                "dir": "ltr",
            }
        ),
        error_messages={
            "required": "لطفاً کد ملی را وارد کنید.",
            "min_length": "کد ملی باید ۱۰ رقم باشد.",
            "max_length": "کد ملی باید ۱۰ رقم باشد.",
        },
    )

    # -------------------------
    # سال تولد
    # -------------------------

    birth_year = forms.ChoiceField(
        label="سال",
        required=True,
        choices=[],
        widget=forms.Select(
            attrs={
                "class": "form-input birth-select",
            }
        ),
        error_messages={
            "required": "لطفاً سال تولد را انتخاب کنید.",
        },
    )

    # -------------------------
    # ماه تولد
    # -------------------------

    birth_month = forms.ChoiceField(
        label="ماه",
        required=True,
        choices=[
            ("1", "۱ - فروردین"),
            ("2", "۲ - اردیبهشت"),
            ("3", "۳ - خرداد"),
            ("4", "۴ - تیر"),
            ("5", "۵ - مرداد"),
            ("6", "۶ - شهریور"),
            ("7", "۷ - مهر"),
            ("8", "۸ - آبان"),
            ("9", "۹ - آذر"),
            ("10", "۱۰ - دی"),
            ("11", "۱۱ - بهمن"),
            ("12", "۱۲ - اسفند"),
        ],
        widget=forms.Select(
            attrs={
                "class": "form-input birth-select",
                "id": "id_birth_month",
            }
        ),
        error_messages={
            "required": "لطفاً ماه تولد را انتخاب کنید.",
        },
    )

    # -------------------------
    # روز تولد
    # -------------------------

    birth_day = forms.ChoiceField(
        label="روز",
        required=True,
        choices=[],
        widget=forms.Select(
            attrs={
                "class": "form-input birth-select",
                "id": "id_birth_day",
            }
        ),
        error_messages={
            "required": "لطفاً روز تولد را انتخاب کنید.",
        },
    )

    # -------------------------
    # فیلد واقعی مدل
    # مخفی است و خود فرم آن را می‌سازد
    # -------------------------

    birth_date = forms.DateField(
        required=False,
        widget=forms.HiddenInput(),
    )

    home_address = forms.CharField(
        label="آدرس منزل",
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "form-input",
                "placeholder": "آدرس کامل منزل",
                "rows": 4,
            }
        ),
        error_messages={
            "required": "لطفاً آدرس منزل را وارد کنید.",
        },
    )

    profile_image = forms.ImageField(
        label="تصویر پروفایل",
        required=True,
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-input",
                "accept": "image/*",
            }
        ),
        error_messages={
            "required": "لطفاً تصویر پروفایل خود را انتخاب کنید.",
            "invalid": "فایل انتخاب‌شده یک تصویر معتبر نیست.",
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
            "father_name",
            "national_code",
            "birth_year",
            "birth_month",
            "birth_day",
            "birth_date",
            "home_address",
            "profile_image",
            "username",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # سال‌های قابل انتخاب
        current_jalali_year = jdatetime.date.today().year

        self.fields["birth_year"].choices = [
            (
                str(year),
                str(year),
            )
            for year in range(
                current_jalali_year,
                current_jalali_year - 120,
                -1,
            )
        ]

        # روزهای اولیه
        self.fields["birth_day"].choices = [
            (
                str(day),
                str(day),
            )
            for day in range(1, 32)
        ]

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if User.objects.filter(
            username=username
        ).exists():
            raise forms.ValidationError(
                "این نام کاربری قبلاً استفاده شده است."
            )

        return username

    def clean_national_code(self):
        code = normalize_digits(
            self.cleaned_data["national_code"]
        )

        code = (
            code
            .replace(" ", "")
            .replace("-", "")
        )

        if len(code) != 10:
            raise forms.ValidationError(
                "کد ملی باید دقیقاً ۱۰ رقم باشد."
            )

        if not code.isdigit():
            raise forms.ValidationError(
                "کد ملی فقط باید شامل عدد باشد."
            )

        if User.objects.filter(
            national_code=code
        ).exists():
            raise forms.ValidationError(
                "این کد ملی قبلاً ثبت شده است."
            )

        return code

    def clean(self):
        cleaned_data = super().clean()

        year = cleaned_data.get("birth_year")
        month = cleaned_data.get("birth_month")
        day = cleaned_data.get("birth_day")

        if year and month and day:
            try:
                year = int(
                    normalize_digits(year)
                )

                month = int(
                    normalize_digits(month)
                )

                day = int(
                    normalize_digits(day)
                )

                # ساخت تاریخ شمسی
                jalali_date = jdatetime.date(
                    year,
                    month,
                    day,
                )

                gregorian_date = (
                    jalali_date.togregorian()
                )

                # تولد نمی‌تواند آینده باشد
                if gregorian_date > timezone.localdate():
                    self.add_error(
                        "birth_year",
                        "تاریخ تولد نمی‌تواند در آینده باشد.",
                    )
                else:
                    cleaned_data["birth_date"] = (
                        gregorian_date
                    )

            except (ValueError, TypeError):
                self.add_error(
                    "birth_day",
                    "تاریخ تولد انتخاب‌شده معتبر نیست.",
                )

        return cleaned_data

    def clean_password2(self):
        password1 = self.cleaned_data.get(
            "password1"
        )

        password2 = self.cleaned_data.get(
            "password2"
        )

        if (
            password1
            and password2
            and password1 != password2
        ):
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

    birth_date = forms.CharField(
        label="تاریخ تولد",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-input jalali-date-input",
                "placeholder": "۱۴۰۰/۰۱/۰۱",
                "inputmode": "numeric",
                "autocomplete": "bday",
                "dir": "ltr",
                "maxlength": "10",
            }
        ),
    )

    class Meta:
        model = User

        fields = (
            "first_name",
            "last_name",
            "father_name",
            "birth_date",
            "home_address",
            "profile_image",
        )

        labels = {
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "father_name": "نام پدر",
            "home_address": "آدرس منزل",
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
            "father_name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "نام پدر",
                }
            ),
            "home_address": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "placeholder": "آدرس منزل",
                    "rows": 4,
                }
            ),
            "profile_image": forms.ClearableFileInput(
                attrs={
                    "class": "form-input",
                    "accept": "image/*",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.birth_date:
            self.initial["birth_date"] = (
                gregorian_to_jalali(
                    self.instance.birth_date
                )
            )

    def clean_birth_date(self):
        value = self.cleaned_data.get(
            "birth_date"
        )

        if not value:
            return None

        try:
            birth_date = jalali_to_gregorian(
                value
            )
        except (ValueError, TypeError):
            raise forms.ValidationError(
                "تاریخ تولد را به صورت شمسی و در قالب ۱۴۰۰/۰۱/۰۱ وارد کنید."
            )

        if birth_date > timezone.localdate():
            raise forms.ValidationError(
                "تاریخ تولد نمی‌تواند در آینده باشد."
            )

        return birth_date


class CustomPasswordChangeForm(
    PasswordChangeForm
):

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
        old_password = self.cleaned_data.get(
            "old_password"
        )

        if not self.user.check_password(
            old_password
        ):
            raise forms.ValidationError(
                "رمز عبور فعلی اشتباه است."
            )

        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get(
            "new_password1"
        )

        password2 = self.cleaned_data.get(
            "new_password2"
        )

        if (
            password1
            and password2
            and password1 != password2
        ):
            raise forms.ValidationError(
                "رمز عبور جدید و تکرار آن یکسان نیستند."
            )

        return password2