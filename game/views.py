from django.db import IntegrityError
from django.forms import ValidationError
from django.shortcuts import redirect, render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.urls import reverse

from .models import Acheivement, Feedback, WordUsageExample, Word

# Create your views here.
def home(request):
    context = {}
    return render(request, "home.html", context)

def register(request):
    error = ""
    form_action = "Register"

    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")
    
        try: 
            user = User.objects.get(username=username)
            error = "User with username already exists!"
        except User.DoesNotExist:
            if username == None or password == None:
                error = "Please fillout both fields!"
            else:
                try:
                    validate_password(password)
                except ValidationError as e:
                    error = ', '.join(e.messages)
            if not error:
                try:
                    user = User.objects.create_user(username=username, password=password)
                    login(request, user)
                    return redirect("home")
                except IntegrityError:
                    error = "An error occurred during user creation."

    context = {"error": error, "form_action": form_action}
    return render(request, "auth_form.html", context)

def login(request):
    error = ""
    form_action = "Login"

    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")
    
        if username == None or password == None:
            error = "Please fillout both fields!"
        else:
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("home") 
            else:
                error = "Credentials Maybe Incorrect!"
    context = {"error": error, "form_action": form_action}
    return render(request, "auth_form.html", context)

def logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("home")

def contact(request):
    error = ""

    if request.method == "POST":
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        if subject == None and message == None:
            error = "Make sure to fill both fields!"
        elif len(subject) > 255:
            error = "Subject can not be longer than 255 characters!"
        else:
            feedback = Feedback.objects.create(subject=subject, message=message, given_by=request.user)
            error = "Your feedback has been sucessfully submitted!"

    context = {"error": error}
    return render(request, "ui/contact.html", context)

def admin_panel_feedbacks(request):

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")
    feedbacks = Feedback.objects.order_by("-dealt_with")
    context = {"feedbacks": feedbacks}
    return render(request, "admin_panel/feedbacks.html", context)

def dealt_feedback(request, feedback_id):

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    feedback = Feedback.objects.get(id=feedback_id)
    feedback.dealt_with = True
    feedback.save()

    return redirect("admin_panel_feedbacks")

def admin_panel_users(request):

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    admins = User.objects.filter(is_superuser=True)
    staffs = User.objects.filter(is_staff=True, is_superuser=False)
    users = User.objects.filter(is_staff=False)
    context = {"users": users, "staffs": staffs, "admins": admins}
    return render(request, "admin_panel/users.html", context)

def delete_user(request, user_id):

    user = User.objects.get(id=user_id)

    if not request.user.is_superuser and request.user != user and not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":
        user.delete()
        return redirect("admin_panel_users")

    confirmation_action = "Delete"
    item_category = "User"
    item = user.username
    context = {"confirmation_action": confirmation_action, "item_category": item_category, "item": item}
    return render(request, "confirmation.html", context)

def promote_user(request, user_id):

    user = User.objects.get(id=user_id)

    if not request.user.is_superuser:
        return redirect("home")

    if request.method == "POST":
        user.is_staff = True
        user.save()
        return redirect("admin_panel_users")

    confirmation_action = "Promote"
    item_category = "User"
    item = user.username
    context = {"confirmation_action": confirmation_action, "item_category": item_category, "item": item}
    return render(request, "confirmation.html", context)

def demote_user(request, user_id):

    user = User.objects.get(id=user_id)

    if not request.user.is_superuser:
        return redirect("home")

    if request.method == "POST":
        user.is_staff = False
        user.save()
        return redirect("admin_panel_users")

    confirmation_action = "Demote"
    item_category = "User"
    item = user.username
    context = {"confirmation_action": confirmation_action, "item_category": item_category, "item": item}
    return render(request, "confirmation.html", context)

def words(request):

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    words = Word.objects.prefetch_related("wordusageexample_set").all()
    context = {"words": words}
    return render(request, "admin_panel/educational_portion/words/words.html", context)

def view_word(request, word_id):
    word = Word.objects.get(id=word_id)
    context = {"word": word, "word_single_view": True}
    return render(request, "admin_panel/educational_portion/words/word.html", context)

def add_word(request):
    error = ""
    form_action = "Add Word"

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":
        word = request.POST.get("word")
        definition = request.POST.get("definition")
        usage_example = request.POST.get("usage_example")

        if "" in [word, definition, usage_example]:
            error = "Please fill out all the fields."
        elif len(word) > 255:
            error = "Word must not exceed 255 characters."
        else:
            try:
                word = Word.objects.get(word=word)
                error = "Word is already present in the database."
            except Word.DoesNotExist:
                word = Word.objects.create(word=word, definition=definition)
                usage = WordUsageExample.objects.create(associated_word=word, sentence=usage_example)
                return redirect("words")

    context = {"error": error, "form_action": form_action}
    return render(request, "admin_panel/educational_portion/words/word_form.html", context)

def update_word(request, word_id):
    error = ""
    form_action = "Update Word"
    selected_word = Word.objects.get(id=word_id)

    word = selected_word.word 
    definition = selected_word.definition 

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":
        word = request.POST.get("word")
        definition = request.POST.get("definition")

        if "" in [word, definition]:
            error = "Please fill out all the fields."
        elif len(word) > 255:
            error = "Word must not exceed 255 characters."
        else:
            try:
                word = Word.objects.get(word=word)
                error = "Word is already present in the database."
            except Word.DoesNotExist:
                selected_word.word = word
                selected_word.definition = definition
                selected_word.save()
                return redirect("words")

    context = {"error": error, "form_action": form_action, "word": word, "definition": definition}
    return render(request, "admin_panel/educational_portion/words/word_form.html", context)

def delete_word(request, word_id):
    selected_word = Word.objects.get(id=word_id)

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":
        selected_word.delete()
        return redirect("words")

    confirmation_action = "Delete"
    item_category = "Word"
    item = selected_word.word
    context = {"confirmation_action": confirmation_action, "item_category": item_category, "item": item}
    return render(request, "confirmation.html", context)

def add_usage_example(request, word_id):
    error = ""
    form_action = "Add Usage Example"

    word = Word.objects.get(id=word_id)

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":
        usage_example = request.POST.get("usage_example")

        if usage_example == None:
            error = "Please fill out the field."
        else:
            try:
                usage_example = WordUsageExample.objects.get(sentence=usage_example, associated_word=word)
                error = "Usage Example is already present for the word."
            except WordUsageExample.DoesNotExist:
                usage_example = WordUsageExample.objects.create(sentence=usage_example, associated_word=word)
                redirect_url = reverse("word", kwargs={"word_id": word_id})
                return redirect(redirect_url)

    context = {"error": error, "form_action": form_action}
    return render(request, "admin_panel/educational_portion/words/word_form.html", context)    

def update_usage_example(request, word_id, usage_example_id):
    error = ""
    form_action = "Update Usage Example"
    selected_usage_example = WordUsageExample.objects.get(id=usage_example_id)

    usage_example = selected_usage_example.sentence 

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":
        usage_example = request.POST.get("usage_example")

        if usage_example == None:
            error = "Please fill out the field."
        else:
            try:
                usage_example = WordUsageExample.objects.get(sentence=usage_example, associated_word=selected_usage_example.associated_word)
                error = "Usage Example is already present for the word."
            except WordUsageExample.DoesNotExist:
                selected_usage_example.sentence = usage_example
                selected_usage_example.save()
                redirect_url = reverse("word", kwargs={"word_id": word_id})
                return redirect(redirect_url)

    context = {"error": error, "form_action": form_action, "usage_example": usage_example}
    return render(request, "admin_panel/educational_portion/words/word_form.html", context)    

def delete_usage_example(request, word_id, usage_example_id):
    selected_usage_example = WordUsageExample.objects.get(id=usage_example_id)

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":
        selected_usage_example.delete()
        redirect_url = reverse("word", kwargs={"word_id": word_id})
        return redirect(redirect_url)

    confirmation_action = "Delete"
    item_category = "Usage Example"
    item = selected_usage_example.sentence
    context = {"confirmation_action": confirmation_action, "item_category": item_category, "item": item}
    return render(request, "confirmation.html", context)

def acheivements(request):

    pointy_acheivements = Acheivement.objects.filter(associated_trivia=None)
    trivia_acheivements = Acheivement.objects.filter(points_required=None)
    context = {"pointy_acheivements": pointy_acheivements, "trivia_acheivements": trivia_acheivements}
    return render(request, "admin_panel/educational_portion/acheivements/acheivements.html", context)

def add_acheivement(request):
    error = ""
    form_action = "Add"

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":
        name = request.POST.get("name")
        points = request.POST.get("points")

        if "" in [name, points]:
            error = "Please fill out all the fields."
        elif len(name) > 255:
            error = "Name must not exceed 255 characters."
        else:
            try:
                acheivement = Acheivement.objects.get(points_required=points)
                error = f"Acheivement for {points} is already present."
            except Acheivement.DoesNotExist:
                acheivement = Acheivement.objects.create(name=name, points_required=points, associated_trivia=None)
                return redirect("acheivements")

    context = {"error": error, "form_action": form_action}
    return render(request, "admin_panel/educational_portion/acheivements/acheivement_form.html", context)

def update_acheivement(request, acheivement_id):
    error = ""
    form_action = "Update"

    acheivement = Acheivement.objects.get(id=acheivement_id)

    if acheivement.associated_trivia:
        is_trivial_acheivement = True
    else:
        is_trivial_acheivement = False

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":
        name = request.POST.get("name")
        if not is_trivial_acheivement:
            points = request.POST.get("points")

        if name == None:
            error = "Please fill out all the fields."
        elif not is_trivial_acheivement:
            if points == None:
                error = "Please fill out all the fields."
        
        if not error:
            if len(name) > 255:
                error = "Name must not exceed 255 characters."
            else:
                try:
                    if not is_trivial_acheivement:
                        acheivement = Acheivement.objects.get(points_required=points)
                        error = f"Acheivement for {points} points is already present."
                    else:
                        acheivement = Acheivement.objects.get(name=name)
                        error = f"Acheivement with the same name is already present."
                except Acheivement.DoesNotExist:
                    acheivement.name = name
                    if not is_trivial_acheivement:
                        acheivement.points_required = points
                    acheivement.save()
                    return redirect("acheivements")

    context = {"error": error, "form_action": form_action, "is_trivial_acheivement": is_trivial_acheivement}
    return render(request, "admin_panel/educational_portion/acheivements/acheivement_form.html", context)

def delete_acheivement(request, acheivement_id):
    acheivement = Acheivement.objects.get(id=acheivement_id)

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":
        acheivement.delete()
        return redirect("acheivements")

    confirmation_action = "Delete"
    item_category = "Acheivement"
    item = acheivement.name
    context = {"confirmation_action": confirmation_action, "item_category": item_category, "item": item}
    return render(request, "confirmation.html", context)