from django.db import IntegrityError
from django.forms import ValidationError
from django.shortcuts import redirect, render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import Feedback

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