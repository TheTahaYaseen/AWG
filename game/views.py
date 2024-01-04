import random
from django.db import IntegrityError
from django.forms import ValidationError
from django.shortcuts import redirect, render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.urls import reverse
from django.db.models import Sum
from .models import Acheivement, AcheivementsUnlocked, Feedback, PointsRecord, Trivia, TriviaQuestion, WordUsageExample, Word

# Create your views here.
def home_view(request):
    context = {}
    return render(request, "home.html", context)

def register_view(request):
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
                    login(request, user=user)
                    return redirect("home")
                except IntegrityError:
                    error = "An error occurred during user creation."

    context = {"error": error, "form_action": form_action}
    return render(request, "auth_form.html", context)

def login_view(request):
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
                login(request, user=user)
                return redirect("home") 
            else:
                error = "Credentials Maybe Incorrect!"
    context = {"error": error, "form_action": form_action}
    return render(request, "auth_form.html", context)

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("home")

def select_difficulty_view(request):
    difficulties = ["Hard", "Medium", "Easy"]

    if request.method == "POST":
        difficulty = request.POST.get("difficulty")
        return redirect("/find_a_word?difficulty=" + str(difficulty))

    context = {"difficulties": difficulties}
    return render(request, "ui/difficulty_form.html", context)

def find_a_word_view(request):
    word = request.session.get("word", None)
    word_blank = request.session.get("word_blank", None)
    attempts = request.session.get("attempts", None)
    game_context = request.session.get("game_context", None)

    error = ""

    if word is None or word_blank is None or attempts is None or game_context is None:
        difficulty = request.GET.get("difficulty", "Easy")

        word_obj = Word.objects.order_by("?").first()

        attempts = 7
        game_context = "You Have {attempts} Attempts!\n"

        if difficulty == "Easy":
            definition = word_obj.definition
            usage_example = WordUsageExample.objects.filter(associated_word=word_obj).first().sentence
            game_context += f"The Word's Definition Is {definition}!\nIts Usage Example Is {usage_example}."
        elif difficulty == "Medium":
            usage_example = WordUsageExample.objects.filter(associated_word=word_obj).first().sentence
            game_context += f"The Word's Usage Example Is {usage_example}."

        word = word_obj.word
        word_blank = ["_"] * len(word)

        # Update session with new values
        request.session["word"] = word
        request.session["word_blank"] = word_blank
        request.session["attempts"] = attempts
        request.session["game_context"] = game_context
        request.session.modified = True

    if request.method == "POST":
        word_guess = request.POST.get("word_guess")

        attempts -= 1

        if attempts == 0:
            request.session.pop("word", None)
            request.session.pop("word_blank", None)
            request.session.pop("attempts", None)
            request.session.pop("game_context", None)
            request.session.modified = True
            game_context = "Loser! You Lost As You Ran Out Of Attempts!"
        else:
            if word_guess == "":
                error = "You cannot leave the word guess empty!"
            elif len(word_guess) != len(word):
                error = "Word guess must be of the same length as the word!"
            else:
                for index, letter in enumerate(word_guess):
                    if letter == word[index]:
                        word_blank[index] = letter
                    elif letter in word and letter not in word_blank:
                        word_blank[index] = f"({letter})"

                if "".join(word_blank) == word:
                    request.session.pop("word", None)
                    request.session.pop("word_blank", None)
                    request.session.pop("attempts", None)
                    request.session.pop("game_context", None)
                    request.session.modified = True

                    points_record = PointsRecord.objects.create(
                        associated_user = request.user,
                        associated_trivia = None,
                        points = 5
                    )

                    return redirect("word_game_win") 
                else:
                    request.session["word_blank"] = word_blank
                    request.session["attempts"] = attempts
                    request.session["game_context"] = game_context
                    request.session.modified = True

    game_context = game_context.replace("{attempts}", str(attempts))
    context = {"word_blank": "".join(word_blank), "game_context": game_context, "error": error}
    return render(request, "ui/find_a_word.html", context)

def word_game_win_view(request):
    points = PointsRecord.objects.all().aggregate(total_points=Sum("points"))["total_points"] or 0
    acheivements_unlocked = AcheivementsUnlocked.objects.filter(associated_user = request.user).values_list("associated_acheivement", flat=True)
    acheivements_to_be_unlocked = Acheivement.objects.filter(associated_trivia = None, points_required__lte=points).exclude(id__in=acheivements_unlocked)
    
    message_heading = f"Congratulations!"
    message = f"You Won The Game! An Addition Of 5 Points Has Been Made! Now You Have {points} Points"

    if acheivements_to_be_unlocked:
        message = f"{message} & Have Unlocked:"

    for acheivement_to_be_unlocked in acheivements_to_be_unlocked:
        acheivement_unlocked = AcheivementsUnlocked.objects.create(
            associated_user=request.user,
            associated_acheivement=acheivement_to_be_unlocked,
        )
        message = f"{message} The {acheivement_to_be_unlocked.name} Acheivement With {acheivement_to_be_unlocked.points_required} Points;"

    context = {"message_heading": message_heading, "message": message}
    return render(request, "ui/message.html", context)

def contact_view(request):
    error = ""

    if request.method == "POST":
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        if subject == None and message == None:
            error = "Make sure to fill both fields!"
        elif len(subject) > 255:
            error = "Subject can not be longer than 255 characters!"
        else:
            feedback = Feedback.objects.create(subject=subject, message=message, given_by=request.user, dealt_with=False)
            error = "Your feedback has been sucessfully submitted!"

    context = {"error": error}
    return render(request, "ui/contact.html", context)

def admin_panel_feedbacks_view(request):

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")
    feedbacks = Feedback.objects.order_by("dealt_with").order_by("-created")
    context = {"feedbacks": feedbacks}
    return render(request, "admin_panel/feedbacks.html", context)

def dealt_feedback_view(request, feedback_id):

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    feedback = Feedback.objects.get(id=feedback_id)
    feedback.dealt_with = True
    feedback.save()

    return redirect("admin_panel_feedbacks")

def admin_panel_users_view(request):

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    admins = User.objects.filter(is_superuser=True)
    staffs = User.objects.filter(is_staff=True, is_superuser=False)
    users = User.objects.filter(is_staff=False)
    context = {"users": users, "staffs": staffs, "admins": admins}
    return render(request, "admin_panel/users.html", context)

def delete_user_view(request, user_id):

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

def promote_user_view(request, user_id):

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

def demote_user_view(request, user_id):

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

def words_view(request):

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    words = Word.objects.prefetch_related("wordusageexample_set").all()
    context = {"words": words}
    return render(request, "admin_panel/educational_portion/words/words.html", context)

def view_word_view(request, word_id):
    word = Word.objects.get(id=word_id)
    context = {"word": word, "word_single_view": True}
    return render(request, "admin_panel/educational_portion/words/word.html", context)

def add_word_view(request):
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

def update_word_view(request, word_id):
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
                redirect_url = reverse("word", kwargs={"word_id": word_id})
                return redirect(redirect_url)

    context = {"error": error, "form_action": form_action, "word": word, "definition": definition}
    return render(request, "admin_panel/educational_portion/words/word_form.html", context)

def delete_word_view(request, word_id):
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

def add_usage_example_view(request, word_id):
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

def update_usage_example_view(request, word_id, usage_example_id):
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

def delete_usage_example_view(request, word_id, usage_example_id):
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

def acheivements_view(request):

    pointy_acheivements = Acheivement.objects.filter(associated_trivia=None)
    trivia_acheivements = Acheivement.objects.filter(points_required=None)
    context = {"pointy_acheivements": pointy_acheivements, "trivia_acheivements": trivia_acheivements}
    return render(request, "admin_panel/educational_portion/acheivements/acheivements.html", context)

def add_acheivement_view(request):
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

def update_acheivement_view(request, acheivement_id):
    error = ""
    form_action = "Update"

    acheivement = Acheivement.objects.get(id=acheivement_id)

    name = acheivement.name

    if acheivement.associated_trivia:
        is_trivial_acheivement = True
    else:
        is_trivial_acheivement = False
        points = acheivement.points_required


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

    context = {"error": error, "form_action": form_action, "is_trivial_acheivement": is_trivial_acheivement, "name": name, "points": points}
    return render(request, "admin_panel/educational_portion/acheivements/acheivement_form.html", context)

def delete_acheivement_view(request, acheivement_id):
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

def trivias_view(request):

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    trivias = Trivia.objects.prefetch_related("triviaquestion_set").all()
    context = {"trivias": trivias}
    return render(request, "admin_panel/educational_portion/trivias/trivias.html", context)

def view_trivia_view(request, trivia_id):
    trivia = Trivia.objects.get(id=trivia_id)
    context = {"trivia": trivia, "trivia_single_view": True}
    return render(request, "admin_panel/educational_portion/trivias/trivia.html", context)

def add_trivia_view(request):
    error = ""
    form_action = "Add Trivia"

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":
        name = request.POST.get("name")
        acheivement_name = request.POST.get("acheivement_name")
        question = request.POST.get("question")
        answer_a = request.POST.get("answer_a")
        answer_b = request.POST.get("answer_b")
        answer_c = request.POST.get("answer_c")
        correct_answer = request.POST.get("correct_answer")
        worth_in_points = request.POST.get("worth_in_points")

        fields_with_max_chars = {
            "name": name,
            "acheivement_name": acheivement_name,
            "question": question,
            "answer_a": answer_a,
            "answer_b": answer_b,
            "answer_c": answer_c,
            "correct_answer": correct_answer
        }

        if "" in [name, question, answer_a, answer_b, answer_c, correct_answer, worth_in_points]:
            error = "Please fill out all the fields. (Except acheivement name if you don't want any)"
        else:
            for field in fields_with_max_chars:
                field_value = fields_with_max_chars[field]
                if len(field_value) > 255:
                    if field == "acheivement_name" and acheivement_name == None:
                        pass
                    else:
                        error = f"{field} cannot be longer than 255 characters."

        if not error:
            try:
                trivia = Trivia.objects.get(name=name)
                error = "Trivia is already present in the database."
            except Trivia.DoesNotExist:
                trivia = Trivia.objects.create(name=name)
                trivia_question = TriviaQuestion.objects.create(question=question, answer_a=answer_a, answer_b=answer_b, answer_c=answer_c, correct_answer=correct_answer, worth_in_points=worth_in_points, associated_trivia=trivia)
                acheivement = Acheivement.objects.create(name=acheivement_name, associated_trivia=trivia, points_required=None)
                return redirect("trivias")

    context = {"error": error, "form_action": form_action}
    return render(request, "admin_panel/educational_portion/trivias/trivia_form.html", context)

def update_trivia_view(request, trivia_id):
    error = ""
    form_action = "Update Trivia"

    trivia = Trivia.objects.get(id=trivia_id)
    name = trivia.name

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":
        name = request.POST.get("name")

        if name == None:
            error = "Please fill out the name field."
        elif len(name) > 255:
            error = "Please make sure the name is shorter than 255 characters."
        else:
            trivia.name = name
            trivia.save()
            redirect_url = reverse("trivia", kwargs={"trivia_id": trivia_id})
            return redirect(redirect_url)

    context = {"error": error, "form_action": form_action, "name": name}
    return render(request, "admin_panel/educational_portion/trivias/trivia_form.html", context)

def delete_trivia_view(request, trivia_id):
    trivia = Trivia.objects.get(id=trivia_id)

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":
        trivia.delete()
        return redirect("trivias")

    confirmation_action = "Delete"
    item_category = "Trivia"
    item = trivia.name
    context = {"confirmation_action": confirmation_action, "item_category": item_category, "item": item}
    return render(request, "confirmation.html", context)

def add_trivia_question_view(request, trivia_id):
    error = ""
    form_action = "Add Trivia Question"

    associated_trivia = Trivia.objects.get(id=trivia_id)

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":
        question = request.POST.get("question")
        answer_a = request.POST.get("answer_a")
        answer_b = request.POST.get("answer_b")
        answer_c = request.POST.get("answer_c")
        correct_answer = request.POST.get("correct_answer")
        worth_in_points = request.POST.get("worth_in_points")

        fields_with_max_chars = {
            "question": question,
            "answer_a": answer_a,
            "answer_b": answer_b,
            "answer_c": answer_c,
            "correct_answer": correct_answer
        }

        if "" in [question, answer_a, answer_b, answer_c, correct_answer, worth_in_points]:
            error = "Please fill out all the fields."
        else:
            for field in fields_with_max_chars:
                field_value = fields_with_max_chars[field]
                if len(field_value) > 255:
                    error = f"{field} cannot be longer than 255 characters."

        if not error:
            try:
                trivia_question = TriviaQuestion.objects.get(question=question, associated_trivia=associated_trivia)
                error = "Trivia Question is already present in the database."
            except TriviaQuestion .DoesNotExist:
                trivia_question = TriviaQuestion.objects.create(question=question, answer_a=answer_a, answer_b=answer_b, answer_c=answer_c, correct_answer=correct_answer, worth_in_points=worth_in_points, associated_trivia=associated_trivia)
                redirect_url = reverse("trivia", kwargs={"trivia_id": trivia_id})
                return redirect(redirect_url)

    context = {"error": error, "form_action": form_action}
    return render(request, "admin_panel/educational_portion/trivias/trivia_form.html", context)

def update_trivia_question_view(request, trivia_id, trivia_question_id):
    error = ""
    form_action = "Update Trivia Question"

    trivia = Trivia.objects.get(id=trivia_id)
    trivia_question = TriviaQuestion.objects.get(id=trivia_question_id)
    
    question = trivia_question.question
    answer_a = trivia_question.answer_a
    answer_b = trivia_question.answer_b
    answer_c = trivia_question.answer_c
    correct_answer = trivia_question.correct_answer
    worth_in_points = trivia_question.worth_in_points

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":
        question = request.POST.get("question")
        answer_a = request.POST.get("answer_a")
        answer_b = request.POST.get("answer_b")
        answer_c = request.POST.get("answer_c")
        correct_answer = request.POST.get("correct_answer")
        worth_in_points = request.POST.get("worth_in_points")

        fields_with_max_chars = {
            "question": question,
            "answer_a": answer_a,
            "answer_b": answer_b,
            "answer_c": answer_c,
            "correct_answer": correct_answer
        }

        if "" in [question, answer_a, answer_b, answer_c, correct_answer, worth_in_points]:
            error = "Please fill out all the fields."
        else:
            for field in fields_with_max_chars:
                field_value = fields_with_max_chars[field]
                if len(field_value) > 255:
                    error = f"{field} cannot be longer than 255 characters."
        if not error:
            trivia_question.question = question
            trivia_question.answer_a = answer_a
            trivia_question.answer_b = answer_b
            trivia_question.answer_c = answer_c
            trivia_question.correct_answer = correct_answer
            trivia_question.worth_in_points = worth_in_points

            redirect_url = reverse("trivia", kwargs={"trivia_id": trivia_id})
            return redirect(redirect_url)

    context = {"error": error, "form_action": form_action, "question": question, "answer_a": answer_a, "answer_b": answer_b, "answer_c": answer_c, "correct_answer": correct_answer, "worth_in_points": worth_in_points}
    return render(request, "admin_panel/educational_portion/trivias/trivia_form.html", context)

def delete_trivia_question_view(request, trivia_id, trivia_question_id):

    trivia = Trivia.objects.get(id=trivia_id)
    trivia_question = TriviaQuestion.objects.get(id=trivia_question_id)

    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":
        trivia_question.delete()
        redirect_url = reverse("trivia", kwargs={"trivia_id": trivia_id})
        return redirect(redirect_url)

    confirmation_action = "Delete"
    item_category = "Trivia Question"
    item = f'"{trivia_question.question}"'
    context = {"confirmation_action": confirmation_action, "item_category": item_category, "item": item}
    return render(request, "confirmation.html", context)
