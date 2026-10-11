from django.shortcuts import get_object_or_404, render, redirect
from django.db import models
from django.db.models import Count, ExpressionWrapper, F, IntegerField, Q,Avg,FloatField
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import *
from decimal import Decimal, InvalidOperation
from .forms import BookReviewForm
from django.db.models.functions import Coalesce




def home(request):
    books = (
        Book.objects
        .select_related(
            "category",
            "subject",
            "publisher",
            "location",
        )
        .prefetch_related(
            "authors",
            "translators",
        )
        .annotate(
            average_rating=Avg("reviews__rating"),
            review_count=Count(
                "reviews",
                distinct=True,
            ),
        )
        .order_by(
            "-average_rating",
            "-review_count",
            "-created_at",
        )[:4]
    )

    return render(
        request,
        "blog/home.html",
        {
            "books": books,
        },
    )


def books(request):
    query = request.GET.get("q", "").strip()
    search_field = request.GET.get("search_field", "all").strip()

    category_id = request.GET.get("category", "").strip()
    subject_id = request.GET.get("subject", "").strip()
    publisher_id = request.GET.get("publisher", "").strip()
    author_id = request.GET.get("author", "").strip()
    translator_id = request.GET.get("translator", "").strip()

    availability = request.GET.get("availability", "").strip()
    sort = request.GET.get("sort", "newest").strip()

    year_from = request.GET.get("year_from", "").strip()
    year_to = request.GET.get("year_to", "").strip()
    price_min = request.GET.get("price_min", "").strip()
    price_max = request.GET.get("price_max", "").strip()

    books_queryset = (
        Book.objects
        .select_related(
            "category",
            "subject",
            "publisher",
            "location",
        )
        .prefetch_related(
            "authors",
            "translators",
        )
        .annotate(
            average_rating=Coalesce(
                Avg("reviews__rating"),
                0.0,
                output_field=FloatField(),
            ),
            review_count=Count(
                "reviews",
                distinct=True,
            ),
        )
    )

    categories = Category.objects.all()
    subjects = Subject.objects.all()
    publishers = Publisher.objects.all()
    authors = Author.objects.all()
    translators = Translator.objects.all()

    # جستجو بر اساس فیلد انتخاب‌شده
    search_fields = {
        "title": Q(title__icontains=query),
        "author": (
            Q(author__icontains=query)
            | Q(authors__name__icontains=query)
        ),
        "translator": Q(translators__name__icontains=query),
        "subject": Q(subject__name__icontains=query),
        "publisher": Q(publisher__name__icontains=query),
        "category": Q(category__name__icontains=query),
        "isbn": Q(isbn__icontains=query),
        "description": Q(description__icontains=query),
        "location": Q(location__code__icontains=query),
    }

    if query:
        if search_field == "all":
            search_condition = (
                Q(title__icontains=query)
                | Q(author__icontains=query)
                | Q(authors__name__icontains=query)
                | Q(translators__name__icontains=query)
                | Q(subject__name__icontains=query)
                | Q(publisher__name__icontains=query)
                | Q(category__name__icontains=query)
                | Q(isbn__icontains=query)
                | Q(description__icontains=query)
                | Q(location__code__icontains=query)
            )
            books_queryset = books_queryset.filter(search_condition)

        elif search_field in search_fields:
            books_queryset = books_queryset.filter(
                search_fields[search_field]
            )

        else:
            books_queryset = books_queryset.filter(
                Q(title__icontains=query)
                | Q(author__icontains=query)
            )

    # فیلتر دسته‌بندی
    if category_id.isdigit():
        books_queryset = books_queryset.filter(
            category_id=int(category_id)
        )

    # فیلتر موضوع
    if subject_id.isdigit():
        books_queryset = books_queryset.filter(
            subject_id=int(subject_id)
        )

    # فیلتر ناشر
    if publisher_id.isdigit():
        books_queryset = books_queryset.filter(
            publisher_id=int(publisher_id)
        )

    # فیلتر نویسنده
    if author_id.isdigit():
        books_queryset = books_queryset.filter(
            authors__id=int(author_id)
        )

    # فیلتر مترجم
    if translator_id.isdigit():
        books_queryset = books_queryset.filter(
            translators__id=int(translator_id)
        )

    # فیلتر موجودی
    if availability == "available":
        books_queryset = books_queryset.filter(
            is_available=True
        )

    elif availability == "unavailable":
        books_queryset = books_queryset.filter(
            is_available=False
        )

    # فیلتر سال انتشار
    if year_from.isdigit():
        books_queryset = books_queryset.filter(
            publication_year__gte=int(year_from)
        )

    if year_to.isdigit():
        books_queryset = books_queryset.filter(
            publication_year__lte=int(year_to)
        )

    # فیلتر بازه قیمت
    try:
        if price_min:
            minimum_price = Decimal(price_min)
            if minimum_price >= 0:
                books_queryset = books_queryset.filter(
                    price__gte=minimum_price
                )
    except (InvalidOperation, ValueError):
        price_min = ""

    try:
        if price_max:
            maximum_price = Decimal(price_max)
            if maximum_price >= 0:
                books_queryset = books_queryset.filter(
                    price__lte=maximum_price
                )
    except (InvalidOperation, ValueError):
        price_max = ""

    # حذف نتایج تکراری ناشی از روابط چندبه‌چند
    books_queryset = books_queryset.distinct()

    # مرتب‌سازی
    if sort == "oldest":
        books_queryset = books_queryset.order_by("created_at")

    elif sort == "title_asc":
        books_queryset = books_queryset.order_by("title")

    elif sort == "title_desc":
        books_queryset = books_queryset.order_by("-title")

    elif sort == "best":
        books_queryset = books_queryset.order_by(
            "-average_rating",
            "-review_count",
            "-created_at",
        )

    elif sort == "price_asc":
        books_queryset = books_queryset.order_by(
            "price",
            "-created_at",
        )

    elif sort == "price_desc":
        books_queryset = books_queryset.order_by(
            "-price",
            "-created_at",
        )

    else:
        sort = "newest"
        books_queryset = books_queryset.order_by("-created_at")

    context = {
        "books": books_queryset,
        "categories": categories,
        "subjects": subjects,
        "publishers": publishers,
        "authors": authors,
        "translators": translators,

        "query": query,
        "search_field": search_field,

        "selected_category": category_id,
        "selected_subject": subject_id,
        "selected_publisher": publisher_id,
        "selected_author": author_id,
        "selected_translator": translator_id,

        "availability": availability,
        "sort": sort,

        "year_from": year_from,
        "year_to": year_to,
        "price_min": price_min,
        "price_max": price_max,
    }

    return render(
        request,
        "blog/books.html",
        context,
    )


def book_detail(request, pk):
    book = get_object_or_404(
        Book.objects
        .select_related(
            "category",
            "subject",
            "publisher",
            "location",
        )
        .prefetch_related(
            "authors",
            "translators",
        )
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
            status=Loan.STATUS_BORROWED,
        ).exists()

        user_review = reviews.filter(
            user=request.user
        ).first()

        user_favorite = Favorite.objects.filter(
            user=request.user,
            book=book,
        ).exists()

    context = {
        "book": book,
        "reviews": reviews,
        "average_rating": average_rating,
        "user_can_review": user_can_review,
        "user_review": user_review,
        "user_favorite": user_favorite,
    }

    return render(
        request,
        "blog/book_detail.html",
        context,
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
