from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import UserFollows, Ticket, Review

User = get_user_model()


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nom d\'utilisateur'
        self.fields['email'].label = 'Adresse e-mail'
        self.fields['password1'].label = 'Mot de passe'
        self.fields['password2'].label = 'Confirmation du mot de passe'
        

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nom d\'utilisateur'
        self.fields['password'].label = 'Mot de passe'

class UserFollowForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Nom d'utilisateur à suivre",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Entrez le nom d'utilisateur",
            'autocomplete': 'off'
        })
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if not username:
            raise forms.ValidationError("Veuillez entrer un nom d'utilisateur.")
        
        try:
            user_to_follow = User.objects.get(username=username)
            
            if self.request and self.request.user == user_to_follow:
                raise forms.ValidationError("Vous ne pouvez pas vous suivre vous-même.")
            
            if self.request and UserFollows.objects.filter(
                user=self.request.user,
                followed_user=user_to_follow
            ).exists():
                raise forms.ValidationError(f"Vous suivez déjà {username}.")
            
            return username
        except User.DoesNotExist:
            raise forms.ValidationError(f"L'utilisateur {username} n'existe pas.")
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs) 

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }

class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={'class': 'rating-radio'}),
        label='Note'
    )
    
    class Meta:
        model = Review
        fields = ['headline', 'rating', 'body']
        widgets = {
            'headline': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        } 