from django.contrib import admin

from .models import (
    Book,
    Category,
    Loan,
    BookReview,
    Favorite,
)



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


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "author",
        "category",
        "is_available",
        "created_at",
    )

    list_filter = (
        "is_available",
        "category",
    )

    search_fields = (
        "title",
        "author",
    )


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):

    list_display = (
        "book",
        "user",
        "status",
        "requested_at",
        "approved_at",
        "borrowed_at",
        "due_date",
        "returned_at",
    )

    list_filter = (
        "status",
        "requested_at",
        "approved_at",
        "borrowed_at",
    )

    search_fields = (
        "book__title",
        "book__author",
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__phone_number",
    )

    readonly_fields = (
        "requested_at",
        "approved_at",
        "borrowed_at",
        "returned_at",
    )

    ordering = (
        "-requested_at",
    )







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