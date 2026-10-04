from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),

    path("books/", views.manage_books, name="manage_books"),
    path("books/add/", views.add_book, name="add_book"),
    path("books/<int:pk>/edit/", views.edit_book, name="edit_book"),
    path("books/<int:pk>/delete/", views.delete_book, name="delete_book"),

    path("categories/", views.manage_categories, name="manage_categories"),
    path("categories/add/", views.add_category, name="add_category"),
    path("categories/<int:pk>/edit/", views.edit_category, name="edit_category"),
    path("categories/<int:pk>/delete/", views.delete_category, name="delete_category"),

    path("loans/", views.manage_loans, name="manage_loans"),
    path("loans/create/", views.create_loan, name="create_loan"),
    path("loans/<int:pk>/return/", views.return_loan, name="return_loan"),

    path("users/", views.manage_users, name="manage_users"),
    path("users/<int:pk>/edit/", views.edit_user, name="edit_user"),
    path("users/<int:pk>/toggle-active/", views.toggle_user_active, name="toggle_user_active"),
    path("users/<int:pk>/delete/", views.delete_user, name="delete_user"),
    path("login/", views.dashboard_login, name="dashboard_login"),
]