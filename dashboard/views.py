from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Count, F, Q, ExpressionWrapper, IntegerField
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .decorators import permission_required
from blog.models import Book, Category, Loan


User = get_user_model()


# =========================================================
# ROLE CONSTANTS
# =========================================================

SYSTEM_MANAGER = "مدیر سیستم"
CONTENT_MANAGER = "مدیر محتوا"
USER_MANAGER = "مدیر کاربران"

ROLE_CHOICES = [
    ("system", SYSTEM_MANAGER),
    ("content", CONTENT_MANAGER),
    ("users", USER_MANAGER),
]


# =========================================================
# ROLE HELPERS
# =========================================================

def get_user_roles(user):
    """
    نقش‌های فعلی کاربر را برمی‌گرداند.
    یک کاربر می‌تواند چند نقش داشته باشد.
    """

    if user.is_superuser:
        roles = {SYSTEM_MANAGER}
    else:
        roles = set(
            user.groups.values_list(
                "name",
                flat=True
            )
        )

    return roles


def set_user_roles(user, selected_roles):
    """
    نقش‌های کاربر را بر اساس انتخاب‌های جدید تنظیم می‌کند.

    selected_roles:
        ["system", "content", "users"]
    """

    selected_roles = set(selected_roles)

    system_selected = "system" in selected_roles
    content_selected = "content" in selected_roles
    users_selected = "users" in selected_roles

    # -----------------------------------------
    # مدیر سیستم
    # -----------------------------------------

    if system_selected:
        system_group, _ = Group.objects.get_or_create(
            name=SYSTEM_MANAGER
        )

        user.groups.clear()
        user.groups.add(system_group)

        user.is_staff = True
        user.is_superuser = True

    # -----------------------------------------
    # سایر نقش‌ها
    # -----------------------------------------

    else:
        groups = []

        if content_selected:
            content_group, _ = Group.objects.get_or_create(
                name=CONTENT_MANAGER
            )
            groups.append(content_group)

        if users_selected:
            users_group, _ = Group.objects.get_or_create(
                name=USER_MANAGER
            )
            groups.append(users_group)

        user.groups.set(groups)

        user.is_superuser = False
        user.is_staff = bool(groups)

    user.save(
        update_fields=[
            "is_staff",
            "is_superuser",
        ]
    )


# =========================================================
# DASHBOARD
# =========================================================

@permission_required("accounts.access_dashboard")
def dashboard_home(request):
    books_count = Book.objects.count()

    categories_count = Category.objects.count()

    available_count = (
        Book.objects
        .annotate(
            borrowed_count=Count(
                "loans",
                filter=Q(
                    loans__status=Loan.STATUS_BORROWED
                ),
            )
        )
        .filter(
            total_copies__gt=F("borrowed_count")
        )
        .count()
    )

    unavailable_count = (
        Book.objects
        .annotate(
            borrowed_count=Count(
                "loans",
                filter=Q(
                    loans__status=Loan.STATUS_BORROWED
                ),
            )
        )
        .filter(
            total_copies__lte=F("borrowed_count")
        )
        .count()
    )

    active_loans_count = Loan.objects.filter(
        status=Loan.STATUS_BORROWED
    ).count()

    pending_loans_count = Loan.objects.filter(
        status=Loan.STATUS_PENDING
    ).count()

    latest_books = (
        Book.objects
        .select_related("category")
        .order_by("-created_at")[:5]
    )

    context = {
        "books_count": books_count,
        "categories_count": categories_count,
        "available_count": available_count,
        "unavailable_count": unavailable_count,
        "active_loans_count": active_loans_count,
        "pending_loans_count": pending_loans_count,
        "latest_books": latest_books,
        "can_manage_books": request.user.has_perm(
            "blog.manage_books"
        ),
        "can_manage_categories": request.user.has_perm(
            "blog.manage_categories"
        ),
        "can_manage_loans": request.user.has_perm(
            "blog.manage_loans"
        ),
        "can_manage_users": request.user.has_perm(
            "accounts.change_user"
        ),
    }

    return render(
        request,
        "dashboard/index.html",
        context
    )


# =========================================================
# BOOKS
# =========================================================

@permission_required("blog.manage_books")
def manage_books(request):
    query = request.GET.get("q", "").strip()

    books = (
        Book.objects
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
                output_field=IntegerField()
            )
        )
        .select_related("category")
        .order_by("-created_at")
    )

    if query:
        books = books.filter(
            Q(title__icontains=query)
            | Q(author__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )

    context = {
        "books": books,
        "query": query,
    }

    return render(
        request,
        "dashboard/books.html",
        context
    )


@permission_required("blog.manage_books")
def add_book(request):
    categories = Category.objects.all()

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        author = request.POST.get("author", "").strip()
        category_id = request.POST.get("category", "").strip()
        description = request.POST.get("description", "").strip()
        cover = request.FILES.get("cover")

        total_copies = request.POST.get(
            "total_copies",
            "1"
        ).strip()

        if not title:
            messages.error(
                request,
                "عنوان کتاب را وارد کنید."
            )

            context = {
                "categories": categories,
                "book": None,
            }

            return render(
                request,
                "dashboard/book_form.html",
                context
            )

        if not author:
            messages.error(
                request,
                "نام نویسنده را وارد کنید."
            )

            context = {
                "categories": categories,
                "book": None,
            }

            return render(
                request,
                "dashboard/book_form.html",
                context
            )

        try:
            total_copies = int(total_copies)
        except (TypeError, ValueError):
            messages.error(
                request,
                "تعداد نسخه‌ها باید یک عدد باشد."
            )

            context = {
                "categories": categories,
                "book": None,
            }

            return render(
                request,
                "dashboard/book_form.html",
                context
            )

        if total_copies < 1:
            messages.error(
                request,
                "تعداد نسخه‌ها باید حداقل ۱ باشد."
            )

            context = {
                "categories": categories,
                "book": None,
            }

            return render(
                request,
                "dashboard/book_form.html",
                context
            )

        category = None

        if category_id:
            category = get_object_or_404(
                Category,
                pk=category_id
            )

        Book.objects.create(
            title=title,
            author=author,
            category=category,
            description=description,
            cover=cover,
            total_copies=total_copies,
            is_available=True,
        )

        messages.success(
            request,
            "کتاب با موفقیت اضافه شد."
        )

        return redirect("manage_books")

    context = {
        "categories": categories,
        "book": None,
    }

    return render(
        request,
        "dashboard/book_form.html",
        context
    )


@permission_required("blog.manage_books")
def edit_book(request, pk):
    categories = Category.objects.all()

    if request.method == "POST":
        with transaction.atomic():

            book = get_object_or_404(
                Book.objects.select_for_update(),
                pk=pk
            )

            title = request.POST.get("title", "").strip()
            author = request.POST.get("author", "").strip()
            category_id = request.POST.get("category", "").strip()
            description = request.POST.get("description", "").strip()
            cover = request.FILES.get("cover")

            total_copies = request.POST.get(
                "total_copies",
                str(book.total_copies)
            ).strip()

            if not title:
                messages.error(
                    request,
                    "عنوان کتاب را وارد کنید."
                )

                context = {
                    "categories": categories,
                    "book": book,
                }

                return render(
                    request,
                    "dashboard/book_form.html",
                    context
                )

            if not author:
                messages.error(
                    request,
                    "نام نویسنده را وارد کنید."
                )

                context = {
                    "categories": categories,
                    "book": book,
                }

                return render(
                    request,
                    "dashboard/book_form.html",
                    context
                )

            try:
                total_copies = int(total_copies)
            except (TypeError, ValueError):
                messages.error(
                    request,
                    "تعداد نسخه‌ها باید یک عدد باشد."
                )

                context = {
                    "categories": categories,
                    "book": book,
                }

                return render(
                    request,
                    "dashboard/book_form.html",
                    context
                )

            if total_copies < 1:
                messages.error(
                    request,
                    "تعداد نسخه‌ها باید حداقل ۱ باشد."
                )

                context = {
                    "categories": categories,
                    "book": book,
                }

                return render(
                    request,
                    "dashboard/book_form.html",
                    context
                )

            borrowed_count = Loan.objects.filter(
                book=book,
                status=Loan.STATUS_BORROWED
            ).count()

            if total_copies < borrowed_count:
                messages.error(
                    request,
                    f"تعداد نسخه‌ها نمی‌تواند کمتر از "
                    f"{borrowed_count} نسخه‌ای باشد که در حال حاضر امانت هستند."
                )

                context = {
                    "categories": categories,
                    "book": book,
                }

                return render(
                    request,
                    "dashboard/book_form.html",
                    context
                )

            category = None

            if category_id:
                category = get_object_or_404(
                    Category,
                    pk=category_id
                )

            book.title = title
            book.author = author
            book.category = category
            book.description = description
            book.total_copies = total_copies
            book.is_available = borrowed_count < total_copies

            if cover:
                book.cover = cover

            book.save()

        messages.success(
            request,
            "اطلاعات کتاب با موفقیت ویرایش شد."
        )

        return redirect("manage_books")

    book = get_object_or_404(
        Book,
        pk=pk
    )

    context = {
        "categories": categories,
        "book": book,
    }

    return render(
        request,
        "dashboard/book_form.html",
        context
    )


@permission_required("blog.manage_books")
def delete_book(request, pk):
    book = get_object_or_404(
        Book,
        pk=pk
    )

    if request.method == "POST":
        book.delete()

        messages.success(
            request,
            "کتاب با موفقیت حذف شد."
        )

        return redirect("manage_books")

    context = {
        "book": book,
    }

    return render(
        request,
        "dashboard/book_delete.html",
        context
    )


# =========================================================
# CATEGORIES
# =========================================================

@permission_required("blog.manage_categories")
def manage_categories(request):
    query = request.GET.get(
        "q",
        ""
    ).strip()

    categories = (
        Category.objects
        .all()
        .order_by("name")
    )

    if query:
        categories = categories.filter(
            name__icontains=query
        )

    context = {
        "categories": categories,
        "query": query,
    }

    return render(
        request,
        "dashboard/categories.html",
        context
    )


@permission_required("blog.manage_categories")
def add_category(request):
    if request.method == "POST":
        name = request.POST.get(
            "name",
            ""
        ).strip()

        if not name:
            messages.error(
                request,
                "نام دسته‌بندی را وارد کنید."
            )

            context = {
                "category": None,
            }

            return render(
                request,
                "dashboard/category_form.html",
                context
            )

        Category.objects.create(
            name=name
        )

        messages.success(
            request,
            "دسته‌بندی با موفقیت اضافه شد."
        )

        return redirect("manage_categories")

    context = {
        "category": None,
    }

    return render(
        request,
        "dashboard/category_form.html",
        context
    )


@permission_required("blog.manage_categories")
def edit_category(request, pk):
    category = get_object_or_404(
        Category,
        pk=pk
    )

    if request.method == "POST":
        name = request.POST.get(
            "name",
            ""
        ).strip()

        if not name:
            messages.error(
                request,
                "نام دسته‌بندی را وارد کنید."
            )

            context = {
                "category": category,
            }

            return render(
                request,
                "dashboard/category_form.html",
                context
            )

        category.name = name
        category.save()

        messages.success(
            request,
            "دسته‌بندی با موفقیت ویرایش شد."
        )

        return redirect("manage_categories")

    context = {
        "category": category,
    }

    return render(
        request,
        "dashboard/category_form.html",
        context
    )


@permission_required("blog.manage_categories")
def delete_category(request, pk):
    category = get_object_or_404(
        Category,
        pk=pk
    )

    if request.method == "POST":
        category.delete()

        messages.success(
            request,
            "دسته‌بندی با موفقیت حذف شد."
        )

        return redirect("manage_categories")

    context = {
        "category": category,
    }

    return render(
        request,
        "dashboard/category_delete.html",
        context
    )


# =========================================================
# LOANS
# =========================================================

@permission_required("blog.manage_loans")
def manage_loans(request):
    available_books = (
        Book.objects
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
                output_field=IntegerField()
            )
        )
        .filter(
            available_copies__gt=0
        )
        .select_related("category")
        .order_by("title")
    )

    users = (
        User.objects
        .filter(is_active=True)
        .order_by(
            "first_name",
            "last_name",
            "username",
        )
    )

    loans = (
        Loan.objects
        .filter(
            status=Loan.STATUS_BORROWED
        )
        .select_related(
            "user",
            "book",
            "book__category",
        )
        .order_by("-borrowed_at")
    )

    context = {
        "available_books": available_books,
        "users": users,
        "loans": loans,
    }

    return render(
        request,
        "dashboard/loans.html",
        context
    )


@permission_required("blog.manage_loans")
def create_loan(request):
    if request.method != "POST":
        return redirect("manage_loans")

    book_id = request.POST.get(
        "book_id",
        ""
    ).strip()

    user_id = request.POST.get(
        "user_id",
        ""
    ).strip()

    if not book_id or not user_id:
        messages.error(
            request,
            "ابتدا کتاب و کاربر را انتخاب کنید."
        )

        return redirect("manage_loans")

    with transaction.atomic():

        book = get_object_or_404(
            Book.objects.select_for_update(),
            pk=book_id
        )

        user = get_object_or_404(
            User,
            pk=user_id
        )

        borrowed_count = Loan.objects.filter(
            book=book,
            status=Loan.STATUS_BORROWED
        ).count()

        available_copies = (
            book.total_copies - borrowed_count
        )

        if available_copies <= 0:
            messages.error(
                request,
                f"کتاب «{book.title}» در حال حاضر هیچ نسخه‌ای برای امانت ندارد."
            )

            return redirect("manage_loans")

        active_loan_exists = Loan.objects.filter(
            user=user,
            book=book,
            status=Loan.STATUS_BORROWED
        ).exists()

        if active_loan_exists:
            messages.error(
                request,
                "این کاربر در حال حاضر همین کتاب را در اختیار دارد."
            )

            return redirect("manage_loans")

        now = timezone.now()

        Loan.objects.create(
            user=user,
            book=book,
            status=Loan.STATUS_BORROWED,
            approved_at=now,
            borrowed_at=now,
        )

        borrowed_count += 1

        book.is_available = (
            borrowed_count < book.total_copies
        )

        book.save(
            update_fields=[
                "is_available",
            ]
        )

    messages.success(
        request,
        f"کتاب «{book.title}» با موفقیت به {user.username} امانت داده شد."
    )

    return redirect("manage_loans")


@permission_required("blog.manage_loans")
def return_loan(request, pk):
    if request.method != "POST":
        return redirect("manage_loans")

    with transaction.atomic():

        loan = get_object_or_404(
            Loan.objects
            .select_for_update()
            .select_related(
                "book",
                "user",
            ),
            pk=pk
        )

        if loan.status != Loan.STATUS_BORROWED:
            messages.error(
                request,
                "فقط کتاب‌های امانت‌داده‌شده را می‌توان بازگشت زد."
            )

            return redirect("manage_loans")

        book = Book.objects.select_for_update().get(
            pk=loan.book_id
        )

        now = timezone.now()

        loan.status = Loan.STATUS_RETURNED
        loan.returned_at = now

        loan.save(
            update_fields=[
                "status",
                "returned_at",
            ]
        )

        borrowed_count = Loan.objects.filter(
            book=book,
            status=Loan.STATUS_BORROWED
        ).count()

        book.is_available = (
            borrowed_count < book.total_copies
        )

        book.save(
            update_fields=[
                "is_available",
            ]
        )

    messages.success(
        request,
        "بازگشت کتاب با موفقیت ثبت شد و موجودی کتاب به‌روزرسانی شد."
    )

    return redirect("manage_loans")


# =========================================================
# USERS
# =========================================================

@permission_required("accounts.view_user")
def manage_users(request):
    users = (
        User.objects
        .prefetch_related("groups")
        .annotate(
            active_loans_count=Count(
                "loans",
                filter=Q(
                    loans__status=Loan.STATUS_BORROWED
                ),
            )
        )
        .order_by("-date_joined")
    )

    context = {
        "users": users,
    }

    return render(
        request,
        "dashboard/users.html",
        context
    )


@permission_required("accounts.change_user")
def edit_user(request, pk):
    user = get_object_or_404(
        User,
        pk=pk
    )

    # مدیر کاربران اجازه دستکاری مدیر سیستم را ندارد.

    if user.is_superuser and not request.user.is_superuser:
        messages.error(
            request,
            "شما اجازه ویرایش مدیر سیستم را ندارید."
        )

        return redirect("manage_users")

    can_manage_roles = request.user.has_perm(
        "accounts.manage_roles"
    )

    if request.method == "POST":
        username = request.POST.get(
            "username",
            ""
        ).strip()

        phone_number = request.POST.get(
            "phone_number",
            ""
        ).strip()

        first_name = request.POST.get(
            "first_name",
            ""
        ).strip()

        last_name = request.POST.get(
            "last_name",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        is_active = (
            request.POST.get("is_active") == "on"
        )

        # -----------------------------------------
        # اعتبارسنجی نام کاربری
        # -----------------------------------------

        if not username:
            messages.error(
                request,
                "نام کاربری نمی‌تواند خالی باشد."
            )

            return redirect(
                "edit_user",
                pk=user.pk
            )

        username_exists = (
            User.objects
            .filter(username=username)
            .exclude(pk=user.pk)
            .exists()
        )

        if username_exists:
            messages.error(
                request,
                "این نام کاربری قبلاً استفاده شده است."
            )

            return redirect(
                "edit_user",
                pk=user.pk
            )

        # -----------------------------------------
        # اعتبارسنجی شماره موبایل
        # -----------------------------------------

        if not phone_number:
            messages.error(
                request,
                "شماره موبایل نمی‌تواند خالی باشد."
            )

            return redirect(
                "edit_user",
                pk=user.pk
            )

        if len(phone_number) != 11 or not phone_number.isdigit():
            messages.error(
                request,
                "شماره موبایل باید ۱۱ رقم باشد."
            )

            return redirect(
                "edit_user",
                pk=user.pk
            )

        phone_exists = (
            User.objects
            .filter(phone_number=phone_number)
            .exclude(pk=user.pk)
            .exists()
        )

        if phone_exists:
            messages.error(
                request,
                "این شماره موبایل قبلاً برای کاربر دیگری ثبت شده است."
            )

            return redirect(
                "edit_user",
                pk=user.pk
            )

        # -----------------------------------------
        # اطلاعات عمومی
        # -----------------------------------------

        user.username = username
        user.phone_number = phone_number
        user.first_name = first_name
        user.last_name = last_name

        # -----------------------------------------
        # وضعیت فعال بودن
        # -----------------------------------------

        if user.pk == request.user.pk:
            user.is_active = True

        elif user.is_superuser:
            user.is_active = True

        else:
            user.is_active = is_active

        # -----------------------------------------
        # تصویر پروفایل
        # -----------------------------------------

        profile_image = request.FILES.get(
            "profile_image"
        )

        if profile_image:
            user.profile_image = profile_image

        # -----------------------------------------
        # رمز عبور
        # -----------------------------------------

        if password:
            user.set_password(password)

        # -----------------------------------------
        # نقش‌ها
        # -----------------------------------------

        if can_manage_roles and user.pk != request.user.pk:
            selected_roles = request.POST.getlist(
                "roles"
            )

            # فقط Superuser اجازه اختصاص نقش مدیر سیستم را دارد.

            if (
                "system" in selected_roles
                and not request.user.is_superuser
            ):
                selected_roles.remove("system")

                messages.warning(
                    request,
                    "نقش «مدیر سیستم» فقط توسط مدیر اصلی قابل اختصاص است."
                )

            set_user_roles(
                user,
                selected_roles
            )

        # -----------------------------------------
        # ذخیره اطلاعات
        # -----------------------------------------

        user.save()

        messages.success(
            request,
            "اطلاعات کاربر با موفقیت ویرایش شد."
        )

        return redirect("manage_users")

    current_roles = get_user_roles(user)

    context = {
        "user_obj": user,
        "current_roles": current_roles,
        "role_choices": ROLE_CHOICES,
        "can_manage_roles": can_manage_roles,
    }

    return render(
        request,
        "dashboard/user_form.html",
        context
    )


@permission_required("accounts.change_user")
def toggle_user_active(request, pk):
    if request.method != "POST":
        return redirect("manage_users")

    user = get_object_or_404(
        User,
        pk=pk
    )

    if user.pk == request.user.pk:
        messages.error(
            request,
            "نمی‌توانید حساب کاربری خودتان را غیرفعال کنید."
        )

        return redirect("manage_users")

    if user.is_superuser and not request.user.is_superuser:
        messages.error(
            request,
            "شما اجازه غیرفعال کردن مدیر سیستم را ندارید."
        )

        return redirect("manage_users")

    user.is_active = not user.is_active

    user.save(
        update_fields=[
            "is_active",
        ]
    )

    if user.is_active:
        messages.success(
            request,
            f"حساب «{user.username}» فعال شد."
        )
    else:
        messages.success(
            request,
            f"حساب «{user.username}» غیرفعال شد."
        )

    return redirect("manage_users")


@permission_required("accounts.delete_user")
def delete_user(request, pk):
    if request.method != "POST":
        return redirect("manage_users")

    user = get_object_or_404(
        User,
        pk=pk
    )

    if user.pk == request.user.pk:
        messages.error(
            request,
            "نمی‌توانید حساب کاربری خودتان را حذف کنید."
        )

        return redirect("manage_users")

    if user.is_superuser and not request.user.is_superuser:
        messages.error(
            request,
            "شما اجازه حذف مدیر سیستم را ندارید."
        )

        return redirect("manage_users")

    active_loan_exists = Loan.objects.filter(
        user=user,
        status=Loan.STATUS_BORROWED
    ).exists()

    if active_loan_exists:
        messages.error(
            request,
            "این کاربر هنوز کتاب امانت‌داده‌شده دارد. ابتدا کتاب را پس بگیرید."
        )

        return redirect("manage_users")

    username = user.username

    with transaction.atomic():
        user.delete()

    messages.success(
        request,
        f"کاربر «{username}» با موفقیت حذف شد."
    )

    return redirect("manage_users")


# =========================================================
# DASHBOARD LOGIN
# =========================================================

def dashboard_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard_home")

    if request.method == "GET":
        list(messages.get_messages(request))

    if request.method == "POST":
        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None:
            messages.error(
                request,
                "نام کاربری یا رمز عبور اشتباه است."
            )

            return render(
                request,
                "dashboard/login.html"
            )

        if not user.is_staff:
            messages.error(
                request,
                "شما اجازه دسترسی به پنل مدیریت را ندارید."
            )

            return render(
                request,
                "dashboard/login.html"
            )

        login(request, user)

        return redirect("dashboard_home")

    return render(
        request,
        "dashboard/login.html"
    )