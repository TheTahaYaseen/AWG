from django.shortcuts import redirect, render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User

# Create your views here.
def home_view(request):
    context = {}
    return render(request, "home.html", context)

def register_view(request):
    error = ""
    form_action = "Register"

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
    
        try: 
            user = User.objects.get(username=username)
            error = "User with username already exists!"
        except User.DoesNotExist:
            # Checking if fields are empty
            if "" in [username, password]:
                error = "Please fillout both fields!"
            elif len(password) < 8:
                error = "Please make sure the password is longer than 8 characters!"
            else:
                user = User.objects.create(username=username, password=password)
                login(request, user)
                return redirect("home")

    context = {"error": error, "form_action": form_action}
    return render(request, "auth_form.html", context)

def login_view(request):
    error = ""
    form_action = "Login"

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
    
        # Checking if fields are empty
        if "" in [username, password]:
            error = "Please fillout both fields!"

        else:
            try: 
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                error = "User with username does not exist!"

            try:
                user = User.objects.get(username=username, password=password)
                login(request, user)
                return redirect("home")
            except User.DoesNotExist:
                error = "Credentials maybe incorrect!"

    context = {"error": error, "form_action": form_action}
    return render(request, "auth_form.html", context)

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("home")