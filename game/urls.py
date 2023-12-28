from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),

    path("register", views.register_view, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),

    path("admin_panel/users", views.admin_panel_users_view, name="admin_panel_users"),
    path("admin_panel/users/delete/<str:user_id>", views.delete_user_view, name="delete_user"),
    path("admin_panel/users/promote/<str:user_id>", views.promote_user_view, name="promote_user"),
    path("admin_panel/users/demote/<str:user_id>", views.demote_user_view, name="demote_user"),

]
