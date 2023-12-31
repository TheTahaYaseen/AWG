from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    
    path("contact", views.contact, name="contact"),
    path("admin_panel/feedbacks", views.admin_panel_feedbacks, name="admin_panel_feedbacks"),
    path("admin_panel/feedbacks/dealt/<str:feedback_id>", views.dealt_feedback, name="dealt_feedback"),

    path("admin_panel/users", views.admin_panel_users, name="admin_panel_users"),
    path("admin_panel/users/<str:user_id>/delete", views.delete_user, name="delete_user"),
    path("admin_panel/users/<str:user_id>/promote", views.promote_user, name="promote_user"),
    path("admin_panel/users/<str:user_id>/demote", views.demote_user, name="demote_user"),

    path("admin_panel/educational_portion/words", views.words, name="words"),
    
    path("admin_panel/educational_portion/words/add", views.add_word, name="add_word"),
    path("admin_panel/educational_portion/words/<str:word_id>/update", views.update_word, name="update_word"),
    path("admin_panel/educational_portion/words/<str:word_id>/delete", views.delete_word, name="delete_word"),
    path("admin_panel/educational_portion/words/<str:word_id>/", views.view_word, name="word"),
    
    path("admin_panel/educational_portion/words/<str:word_id>/usage_examples/add", views.add_usage_example, name="add_usage_example"),
    path("admin_panel/educational_portion/words/<str:word_id>/usage_examples/<str:usage_example_id>/update", views.update_usage_example, name="update_usage_example"),
    path("admin_panel/educational_portion/words/<str:word_id>/usage_examples/<str:usage_example_id>/delete", views.delete_usage_example, name="delete_usage_example"),

    path("admin_panel/educational_portion/acheivements", views.acheivements, name="acheivements"),
    
    path("admin_panel/educational_portion/acheivements/add", views.add_acheivement, name="add_acheivement"),
    path("admin_panel/educational_portion/acheivements/<str:acheivement_id>/update", views.update_acheivement, name="update_acheivement"),
    path("admin_panel/educational_portion/acheivements/<str:acheivement_id>/delete", views.delete_acheivement, name="delete_acheivement"),

    path("admin_panel/educational_portion/trivias", views.trivias, name="trivias"),
    path("admin_panel/educational_portion/trivias/add", views.add_trivia, name="add_trivia"),
    path("admin_panel/educational_portion/trivias/<str:trivia_id>", views.view_trivia, name="trivia"),
    path("admin_panel/educational_portion/trivias/<str:trivia_id>/update", views.update_trivia, name="update_trivia"),
    path("admin_panel/educational_portion/trivias/<str:trivia_id>/delete", views.delete_trivia, name="delete_trivia"),
    
    path("admin_panel/educational_portion/trivias/<str:trivia_id>/trivia_questions/add", views.add_trivia_question, name="add_trivia_question"),
    path("admin_panel/educational_portion/trivias/<str:trivia_id>/trivia_questions/<str:trivia_question_id>/update", views.update_trivia_question, name="update_trivia_question"),
    path("admin_panel/educational_portion/trivias/<str:trivia_id>/trivia_questions/<str:trivia_question_id>/delete", views.delete_trivia_question, name="delete_trivia_question"),
]
