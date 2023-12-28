from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    
    path("contact", views.contact, name="contact"),
    path("admin_panel/feedbacks", views.admin_panel_feedbacks, name="admin_panel_feedbacks"),

    path("admin_panel/users", views.admin_panel_users, name="admin_panel_users"),
    path("admin_panel/users/delete/<str:user_id>", views.delete_user, name="delete_user"),
    path("admin_panel/users/promote/<str:user_id>", views.promote_user, name="promote_user"),
    path("admin_panel/users/demote/<str:user_id>", views.demote_user, name="demote_user"),

    path("admin_panel/feedbacks/dealt/<str:feedback_id>", views.dealt_feedback, name="dealt_feedback"),
]
