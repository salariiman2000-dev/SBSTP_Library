from django.contrib import admin

from .models import (
    Book,
    Category,
    Subject,
    Author,
    Translator,
    Publisher,
    BookLocation,
    Loan,
    BookReview,
    Favorite,
)


# =========================================================
# CATEGORY
# =========================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
    )

    search_fields = (
        "name",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }


# =========================================================
# SUBJECT
# =========================================================

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):

    list_display = (
        "name",
    )

    search_fields = (
        "name",
    )


# =========================================================
# AUTHOR
# =========================================================

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):

    list_display = (
        "name",
    )

    search_fields = (
        "name",
    )


# =========================================================
# TRANSLATOR
# =========================================================

@admin.register(Translator)
class TranslatorAdmin(admin.ModelAdmin):

    list_display = (
        "name",
    )

    search_fields = (
        "name",
    )


# =========================================================
# PUBLISHER
# =========================================================

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):

    list_display = (
        "name",
    )

    search_fields = (
        "name",
    )


# =========================================================
# BOOK LOCATION
# =========================================================

@admin.register(BookLocation)
class BookLocationAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "description",
    )

    search_fields = (
        "code",
        "description",
    )


# =========================================================
# BOOK
# =========================================================

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "display_authors",
        "display_translators",
        "category",
        "subject",
        "publisher",
        "publication_year",
        "location",
        "is_available",
        "created_at",
    )

    list_filter = (
        "is_available",
        "category",
        "subject",
        "publisher",
        "publication_year",
    )

    search_fields = (
        "title",
        "authors__name",
        "translators__name",
        "category__name",
        "subject__name",
        "publisher__name",
        "location__code",
    )

    filter_horizontal = (
        "authors",
        "translators",
    )

    @admin.display(
        description="مؤلفان"
    )
    def display_authors(self, obj):
        return ", ".join(
            author.name
            for author in obj.authors.all()
        )

    @admin.display(
        description="مترجمان"
    )
    def display_translators(self, obj):
        return ", ".join(
            translator.name
            for translator in obj.translators.all()
        )


# =========================================================
# LOAN
# =========================================================

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):

    list_display = (
        "registration_number",
        "user",
        "book",
        "borrowed_at",
        "due_date",
        "returned_at",
        "status",
        "late_days",
        "total_fine",
    )

    list_filter = (
        "status",
        "borrowed_at",
        "due_date",
        "returned_at",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "book__title",
    )

    readonly_fields = (
        "registration_number",
        "borrowed_at",
        "returned_at",
        "late_days",
        "total_fine",
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    autocomplete_fields = (
        "user",
        "book",
    )


# =========================================================
# BOOK REVIEW
# =========================================================

@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):

    list_display = (
        "book",
        "user",
        "rating",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "rating",
        "created_at",
    )

    search_fields = (
        "book__title",
        "user__username",
        "comment",
    )

    ordering = (
        "-created_at",
    )


# =========================================================
# FAVORITE
# =========================================================

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "book",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "user__username",
        "book__title",
    )

    ordering = (
        "-created_at",
    )