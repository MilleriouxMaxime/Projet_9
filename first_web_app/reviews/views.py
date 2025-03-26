from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render

from .forms import SignUpForm


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # Ici on crée l'utilisateur
            return redirect("login")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")  # Redirige vers la page d'accueil après connexion
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def home(request):
    return render(request, "home.html")
