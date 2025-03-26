from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(
    AbstractUser
):  # On crée un utilisateur basé sur le modèle existant de Django
    email = models.EmailField(unique=True)  # Ajoute un email unique et obligatoire

    def __str__(self):
        return self.username  # Affiche le nom de l'utilisateur dans l'admin Django
