from django.urls import path

from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("", views.home, name="home"),  # Ajoute aussi une route pour la page d'accueil
]
