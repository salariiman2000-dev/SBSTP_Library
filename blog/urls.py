from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),

    path(
        "books/",
        views.books,
        name="books"
    ),

    path(
        "books/<int:pk>/",
        views.book_detail,
        name="book_detail"
    ),

    path(
        "about/",
        views.about,
        name="about"
    ),

    path(
        "contact/",
        views.contact,
        name="contact"
    ),

    path(
        "books/<int:pk>/review/",
        views.add_book_review,
        name="add_book_review"
    ),

    path(
        "books/<int:pk>/favorite/",
        views.toggle_favorite,
        name="toggle_favorite"
    ),
]