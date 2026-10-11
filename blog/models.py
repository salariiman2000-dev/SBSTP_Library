from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone

# =========================================================
# CATEGORY
# =========================================================

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


# =========================================================
# SUBJECT
# =========================================================

class Subject(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="نام موضوع"
    )

    class Meta:
        verbose_name = "موضوع"
        verbose_name_plural = "موضوعات"
        ordering = ["name"]

    def __str__(self):
        return self.name


# =========================================================
# AUTHOR
# =========================================================

class Author(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="نام مؤلف"
    )

    class Meta:
        verbose_name = "مؤلف"
        verbose_name_plural = "مؤلفان"
        ordering = ["name"]

    def __str__(self):
        return self.name


# =========================================================
# TRANSLATOR
# =========================================================

class Translator(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="نام مترجم"
    )

    class Meta:
        verbose_name = "مترجم"
        verbose_name_plural = "مترجمان"
        ordering = ["name"]

    def __str__(self):
        return self.name


# =========================================================
# PUBLISHER
# =========================================================

class Publisher(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="نام ناشر"
    )

    class Meta:
        verbose_name = "ناشر"
        verbose_name_plural = "ناشران"
        ordering = ["name"]

    def __str__(self):
        return self.name


# =========================================================
# BOOK LOCATION
# =========================================================

class BookLocation(models.Model):
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="کد محل"
    )

    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="توضیحات محل"
    )

    class Meta:
        verbose_name = "محل کتاب"
        verbose_name_plural = "محل‌های کتاب"
        ordering = ["code"]

    def __str__(self):
        return self.code


# =========================================================
# BOOK
# =========================================================

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

    # -----------------------------------------
    # مؤلفان
    # -----------------------------------------

    authors = models.ManyToManyField(
        Author,
        related_name="books",
        verbose_name="مؤلفان",
        blank=False
    )

    # -----------------------------------------
    # مترجمان
    # -----------------------------------------

    translators = models.ManyToManyField(
        Translator,
        related_name="books",
        verbose_name="مترجمان",
        blank=True
    )

    # -----------------------------------------
    # دسته‌بندی
    # -----------------------------------------

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="books",
        verbose_name="دسته‌بندی"
    )

    # -----------------------------------------
    # موضوع
    # -----------------------------------------

    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="books",
        verbose_name="موضوع"
    )

    # -----------------------------------------
    # ناشر
    # -----------------------------------------

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.PROTECT,
        related_name="books",
        verbose_name="ناشر"
    )

    # -----------------------------------------
    # سال انتشار شمسی
    # -----------------------------------------

    publication_year = models.PositiveSmallIntegerField(
        verbose_name="سال انتشار"
    )

    # -----------------------------------------
    # محل قرارگیری
    # -----------------------------------------

    location = models.ForeignKey(
        BookLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="books",
        verbose_name="محل قرارگیری"
    )

    # -----------------------------------------
    # توضیحات
    # -----------------------------------------

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات"
    )

    # -----------------------------------------
    # تصویر جلد
    # -----------------------------------------

    cover = models.ImageField(
        upload_to="books/covers/",
        blank=True,
        null=True,
        verbose_name="تصویر جلد"
    )

    # -----------------------------------------
    # تعداد نسخه‌ها
    # -----------------------------------------

    total_copies = models.PositiveIntegerField(
        default=1,
        verbose_name="تعداد نسخه‌ها"
    )

    # -----------------------------------------
    # وضعیت موجودی
    # -----------------------------------------

    is_available = models.BooleanField(
        default=True,
        verbose_name="موجود است"
    )

    # -----------------------------------------
    # تاریخ ثبت
    # -----------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت"
    )


    isbn = models.CharField(
        "شابک",
        max_length=20,
        unique=True,
        blank=True,
        null=True,
    )

    registration_number = models.PositiveIntegerField(
        "شماره ثبت",
        unique=True,
        editable=False,
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name="قیمت کتاب"
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


    def save(self, *args, **kwargs):
        if not self.registration_number:
            last_book = (
                Book.objects
                .select_for_update()
                .order_by("-registration_number")
                .first()
            )

            if last_book:
                self.registration_number = last_book.registration_number + 1
            else:
                self.registration_number = 1

        super().save(*args, **kwargs)


# =========================================================
# LOAN
# =========================================================

# =========================================================
# LOAN
# =========================================================

class Loan(models.Model):

    STATUS_BORROWED = "borrowed"
    STATUS_AVAILABLE = "available"

    STATUS_CHOICES = [
        (
            STATUS_BORROWED,
            "امانت داده شده",
        ),
        (
            STATUS_AVAILABLE,
            "موجود",
        ),
    ]

    registration_number = models.PositiveIntegerField(
        "شماره ثبت امانت",
        unique=True,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="loans",
        verbose_name="کاربر",
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="loans",
        verbose_name="کتاب",
    )

    status = models.CharField(
        "وضعیت",
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_BORROWED,
    )

    borrowed_at = models.DateTimeField(
        "تاریخ دریافت",
        null=True,
        blank=True,
    )

    due_date = models.DateTimeField(
        "مهلت بازگشت",
        null=True,
        blank=True,
    )

    returned_at = models.DateTimeField(
        "تاریخ برگشت",
        null=True,
        blank=True,
    )

    daily_fine = models.PositiveBigIntegerField(
        "جریمه هر روز",
        default=0,
    )

    late_days = models.PositiveIntegerField(
        "تعداد روز دیرکرد",
        default=0,
    )

    total_fine = models.PositiveBigIntegerField(
        "مبلغ جریمه",
        default=0,
    )

    admin_note = models.TextField(
        "توضیحات مدیر",
        blank=True,
    )

    created_at = models.DateTimeField(
        "تاریخ ثبت",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "امانت"
        verbose_name_plural = "امانت‌ها"
        ordering = ["-created_at"]

        permissions = [
            (
                "manage_loans",
                "مدیریت امانت‌ها",
            ),
        ]

    def __str__(self):
        return (
            f"{self.registration_number} - "
            f"{self.user} - "
            f"{self.book}"
        )

    def save(self, *args, **kwargs):

        if not self.registration_number:

            last_loan = (
                Loan.objects
                .order_by("-registration_number")
                .first()
            )

            if last_loan:
                self.registration_number = (
                    last_loan.registration_number + 1
                )
            else:
                self.registration_number = 1

        super().save(*args, **kwargs)

    @property
    def current_late_days(self):

        if (
            self.status != self.STATUS_BORROWED
            or not self.due_date
        ):
            return self.late_days

        now = timezone.now()

        if now <= self.due_date:
            return 0

        difference = now - self.due_date

        return difference.days

    @property
    def current_fine(self):

        return (
            self.current_late_days *
            self.daily_fine
        )


# =========================================================
# BOOK REVIEW
# =========================================================

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


# =========================================================
# FAVORITE
# =========================================================

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