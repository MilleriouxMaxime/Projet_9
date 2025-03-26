from django import forms
from django.contrib.auth import get_user_model

# Utilisation du modèle personnalisé pour l'utilisateur
User = get_user_model()


class SignUpForm(forms.ModelForm):
    # Définition des champs pour le formulaire d'inscription
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirmation = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")

        # Validation que les mots de passe correspondent
        if password != password_confirmation:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")

        return cleaned_data
