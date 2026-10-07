from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):

    def create_user(
        self,
        username,
        phone_number=None,
        password=None,
        **extra_fields
    ):
        if not username:
            raise ValueError("نام کاربری الزامی است.")

        user = self.model(
            username=username,
            phone_number=phone_number,
            **extra_fields
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        username,
        password=None,
        **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "Superuser باید is_staff=True داشته باشد."
            )

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Superuser باید is_superuser=True داشته باشد."
            )

        return self.create_user(
            username=username,
            password=password,
            **extra_fields
        )