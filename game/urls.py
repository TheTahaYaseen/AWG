from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),

    path("register", views.register_view, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    
    path("contact", views.contact_view, name="contact"),
    path("admin_panel/feedbacks", views.admin_panel_feedbacks_view, name="admin_panel_feedbacks"),
    path("admin_panel/feedbacks/dealt/<str:feedback_id>", views.dealt_feedback_view, name="dealt_feedback"),

    path("admin_panel/users", views.admin_panel_users_view, name="admin_panel_users"),
    path("admin_panel/users/<str:user_id>/delete", views.delete_user_view, name="delete_user"),
    path("admin_panel/users/<str:user_id>/promote", views.promote_user_view, name="promote_user"),
    path("admin_panel/users/<str:user_id>/demote", views.demote_user_view, name="demote_user"),

    path("admin_panel/educational_portion/words", views.words_view, name="words"),
    
    path("admin_panel/educational_portion/words/add", views.add_word_view, name="add_word"),
    path("admin_panel/educational_portion/words/<str:word_id>/update", views.update_word_view, name="update_word"),
    path("admin_panel/educational_portion/words/<str:word_id>/delete", views.delete_word_view, name="delete_word"),
    path("admin_panel/educational_portion/words/<str:word_id>/", views.view_word_view, name="word"),
    
    path("admin_panel/educational_portion/words/<str:word_id>/usage_examples/add", views.add_usage_example_view, name="add_usage_example"),
    path("admin_panel/educational_portion/words/<str:word_id>/usage_examples/<str:usage_example_id>/update", views.update_usage_example_view, name="update_usage_example"),
    path("admin_panel/educational_portion/words/<str:word_id>/usage_examples/<str:usage_example_id>/delete", views.delete_usage_example_view, name="delete_usage_example"),

    path("admin_panel/educational_portion/acheivements", views.acheivements_view, name="acheivements"),
    
    path("admin_panel/educational_portion/acheivements/add", views.add_acheivement_view, name="add_acheivement"),
    path("admin_panel/educational_portion/acheivements/<str:acheivement_id>/update", views.update_acheivement_view, name="update_acheivement"),
    path("admin_panel/educational_portion/acheivements/<str:acheivement_id>/delete", views.delete_acheivement_view, name="delete_acheivement"),

    path("admin_panel/educational_portion/trivias", views.trivias_view, name="trivias"),
    path("admin_panel/educational_portion/trivias/add", views.add_trivia_view, name="add_trivia"),
    path("admin_panel/educational_portion/trivias/<str:trivia_id>", views.view_trivia_view, name="trivia"),
    path("admin_panel/educational_portion/trivias/<str:trivia_id>/update", views.update_trivia_view, name="update_trivia"),
    path("admin_panel/educational_portion/trivias/<str:trivia_id>/delete", views.delete_trivia_view, name="delete_trivia"),
    
    path("admin_panel/educational_portion/trivias/<str:trivia_id>/trivia_questions/add", views.add_trivia_question_view, name="add_trivia_question"),
    path("admin_panel/educational_portion/trivias/<str:trivia_id>/trivia_questions/<str:trivia_question_id>/update", views.update_trivia_question_view, name="update_trivia_question"),
    path("admin_panel/educational_portion/trivias/<str:trivia_id>/trivia_questions/<str:trivia_question_id>/delete", views.delete_trivia_question_view, name="delete_trivia_question"),

    path("find_a_word", views.find_a_word_view, name="find_a_word"),
    path("word_game_win", views.word_game_win_view, name="word_game_win"),
]
