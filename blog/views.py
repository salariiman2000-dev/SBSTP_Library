from django.shortcuts import get_object_or_404, render, redirect
from django.db import models
from django.db.models import Count, ExpressionWrapper, F, IntegerField, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import *

from .forms import BookReviewForm


def home(request):
    books = (
        Book.objects
        .select_related("category")
        .annotate(
            average_rating=models.Avg("reviews__rating"),
            review_count=models.Count("reviews")
        )
        .order_by(
            "-average_rating",
            "-review_count",
            "-created_at"
        )[:4]
    )

    return render(
        request,
        "blog/home.html",
        {
            "books": books,
        }
    )


def books(request):

    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    sort = request.GET.get("sort", "newest").strip()
    availability = request.GET.get("availability", "").strip()

    books = (
        Book.objects
        .select_related("category")
        .annotate(
            average_rating=models.functions.Coalesce(
                models.Avg("reviews__rating"),
                0.0
            ),
            review_count=models.Count("reviews")
        )
    )

    categories = Category.objects.all()

    if query:

        books = books.filter(
            Q(title__icontains=query)
            | Q(author__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )

    if category_id:

        books = books.filter(
            category_id=category_id
        )

    if availability == "available":

        books = books.filter(
            is_available=True
        )

    elif availability == "unavailable":

        books = books.filter(
            is_available=False
        )

    if sort == "best":

        books = books.order_by(
            "-average_rating",
            "-review_count",
            "-created_at"
        )

    elif sort == "oldest":

        books = books.order_by(
            "created_at"
        )

    elif sort == "title_asc":

        books = books.order_by(
            "title"
        )

    elif sort == "title_desc":

        books = books.order_by(
            "-title"
        )

    else:

        books = books.order_by(
            "-created_at"
        )

    return render(
        request,
        "blog/books.html",
        {
            "books": books,
            "categories": categories,
            "query": query,
            "selected_category": category_id,
            "sort": sort,
            "availability": availability,
        }
    )


def book_detail(request, pk):

    book = get_object_or_404(
        Book.objects
        .select_related("category")
        .annotate(
            borrowed_count=Count(
                "loans",
                filter=Q(
                    loans__status=Loan.STATUS_BORROWED
                ),
            )
        )
        .annotate(
            available_copies=ExpressionWrapper(
                F("total_copies") - F("borrowed_count"),
                output_field=IntegerField(),
            )
        ),
        pk=pk,
    )

    reviews = book.reviews.select_related(
        "user"
    ).all()

    average_rating = reviews.aggregate(
        average=models.Avg("rating")
    )["average"]

    user_can_review = False
    user_review = None
    user_favorite = False

    if request.user.is_authenticated:

        user_can_review = Loan.objects.filter(
            user=request.user,
            book=book,
            status=Loan.STATUS_BORROWED
        ).exists()

        user_review = reviews.filter(
            user=request.user
        ).first()

        user_favorite = Favorite.objects.filter(
            user=request.user,
            book=book
        ).exists()

    return render(
        request,
        "blog/book_detail.html",
        {
            "book": book,
            "reviews": reviews,
            "average_rating": average_rating,
            "user_can_review": user_can_review,
            "user_review": user_review,
            "user_favorite": user_favorite,
        }
    )

@login_required
def add_book_review(request, pk):
    book = get_object_or_404(Book,pk=pk)
    has_borrowed = Loan.objects.filter(user=request.user,book=book,status=Loan.STATUS_BORROWED).exists()

    if not has_borrowed:
        messages.error(request,"شما تا وقتی این کتاب را به امانت نگرفته‌اید، حق ثبت امتیاز و نظر برای این کتاب را ندارید.")

        return redirect("book_detail",pk=book.pk)

    review = BookReview.objects.filter(book=book,user=request.user).first()
    is_editing = review is not None

    if request.method == "POST":
        form = BookReviewForm(request.POST,instance=review)

        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()

            if is_editing:
                messages.success(request,"نظر شما با موفقیت ویرایش شد.")

            else:
                messages.success(request,"نظر شما با موفقیت ثبت شد.")

            return redirect("book_detail",pk=book.pk)

    else:
        form = BookReviewForm(instance=review)

    context={
        "book": book,
        "form": form,
        "review": review,
        "is_editing": is_editing,
    }

    return render(request,"blog/book_review.html",context)


@login_required
def toggle_favorite(request, pk):
    book = get_object_or_404(Book, pk=pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user,book=book)

    if created:
        request.session["favorite_notification"] = True
        messages.success(request,"کتاب به علاقه‌مندی‌های شما اضافه شد.")

    else:
        favorite.delete()
        messages.success(request,"کتاب از علاقه‌مندی‌های شما حذف شد.")

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return redirect("book_detail", pk=book.pk)





def about(request):
    return render(request,"blog/about.html")


def contact(request):
    return render(request,"blog/contact.html")
