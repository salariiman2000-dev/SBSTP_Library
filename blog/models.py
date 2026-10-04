from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="نام دسته‌بندی"
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        verbose_name="اسلاگ"
    )

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["name"]

        permissions = [
            (
                "manage_categories",
                "مدیریت دسته‌بندی‌ها",
            ),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(
                self.name,
                allow_unicode=True
            )

            if not base_slug:
                base_slug = "category"

            slug = base_slug
            counter = 2

            while Category.objects.filter(
                slug=slug
            ).exclude(pk=self.pk).exists():

                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class Book(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان کتاب"
    )

    processed_cover = models.ImageField(
        upload_to="books/processed/",
        blank=True,
        null=True,
        verbose_name="جلد پردازش‌شده"
    )

    author = models.CharField(
        max_length=150,
        verbose_name="نویسنده"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="books",
        verbose_name="دسته‌بندی"
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات"
    )

    cover = models.ImageField(
        upload_to="books/covers/",
        blank=True,
        null=True,
        verbose_name="تصویر جلد"
    )

    total_copies = models.PositiveIntegerField(
        default=1,
        verbose_name="تعداد نسخه‌ها"
    )

    is_available = models.BooleanField(
        default=True,
        verbose_name="موجود است"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت"
    )

    class Meta:
        verbose_name = "کتاب"
        verbose_name_plural = "کتاب‌ها"
        ordering = ["-created_at"]

        permissions = [
            (
                "manage_books",
                "مدیریت کتاب‌ها",
            ),
        ]

    def __str__(self):
        return self.title


class Loan(models.Model):

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_BORROWED = "borrowed"
    STATUS_RETURNED = "returned"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (
            STATUS_PENDING,
            "در انتظار تأیید"
        ),
        (
            STATUS_APPROVED,
            "تأیید شده"
        ),
        (
            STATUS_BORROWED,
            "امانت داده شده"
        ),
        (
            STATUS_RETURNED,
            "بازگردانده شده"
        ),
        (
            STATUS_REJECTED,
            "رد شده"
        ),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="loans",
        verbose_name="کاربر"
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="loans",
        verbose_name="کتاب"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name="وضعیت"
    )

    requested_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ درخواست"
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ تأیید"
    )

    borrowed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ تحویل"
    )

    due_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="مهلت بازگشت"
    )

    returned_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ بازگشت"
    )

    admin_note = models.TextField(
        blank=True,
        verbose_name="یادداشت مدیر"
    )

    class Meta:
        verbose_name = "امانت"
        verbose_name_plural = "امانت‌ها"
        ordering = ["-requested_at"]

        permissions = [
            (
                "manage_loans",
                "مدیریت امانت‌ها",
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.book}"







class BookReview(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="کتاب"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="book_reviews",
        verbose_name="کاربر"
    )

    rating = models.PositiveSmallIntegerField(
        verbose_name="امتیاز"
    )

    comment = models.TextField(
        verbose_name="نظر"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین ویرایش"
    )

    class Meta:
        verbose_name = "نظر کتاب"
        verbose_name_plural = "نظرات کتاب"
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["book", "user"],
                name="unique_book_review_per_user"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.book} - {self.rating}"
    







class Favorite(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="کاربر"
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="کتاب"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ افزودن"
    )

    class Meta:
        verbose_name = "علاقه‌مندی"
        verbose_name_plural = "علاقه‌مندی‌ها"
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"],
                name="unique_user_favorite_book"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.book}"