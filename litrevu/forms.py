from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import UserFollows, Ticket, Review

User = get_user_model()


class SignUpForm(UserCreationForm):
    """Custom signup form extending Django's UserCreationForm.

    Adds email field and customizes field labels to French.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        """Initialize the form with custom French labels.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nom d\'utilisateur'
        self.fields['email'].label = 'Adresse e-mail'
        self.fields['password1'].label = 'Mot de passe'
        self.fields['password2'].label = 'Confirmation du mot de passe'
        

class LoginForm(AuthenticationForm):
    """Custom login form extending Django's AuthenticationForm.

    Customizes field labels to French.
    """
    def __init__(self, *args, **kwargs):
        """Initialize the form with custom French labels.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nom d\'utilisateur'
        self.fields['password'].label = 'Mot de passe'

class UserFollowForm(forms.Form):
    """Form for following other users.

    Includes validation to prevent:
    - Self-following
    - Following already followed users
    - Following blocked users
    - Following users who have blocked you
    """
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
        """Validate the username field.

        Performs various checks to ensure the follow relationship is valid:
        - User exists
        - Not trying to follow self
        - Not already following
        - No blocking relationships in either direction

        Returns:
            str: The validated username

        Raises:
            ValidationError: If any validation check fails
        """
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
            
            # Check if the user has blocked the user they're trying to follow
            if self.request and self.request.user.blocking.filter(blocked_user=user_to_follow).exists():
                raise forms.ValidationError("Vous ne pouvez pas suivre un utilisateur que vous avez bloqué.")
            
            # Check if the target user has blocked the current user
            if self.request and user_to_follow.blocking.filter(blocked_user=self.request.user).exists():
                raise forms.ValidationError("Vous ne pouvez pas suivre cet utilisateur car il vous a bloqué.")
            
            return username
        except User.DoesNotExist:
            raise forms.ValidationError(f"L'utilisateur {username} n'existe pas.")
    
    def __init__(self, *args, **kwargs):
        """Initialize the form with request context.

        Stores the request object for use in validation.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments with 'request' key
        """
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs) 

class TicketForm(forms.ModelForm):
    """Form for creating and editing tickets.

    Includes fields for title, description, and optional image.
    All fields use Bootstrap form control classes.
    """
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }

class ReviewForm(forms.ModelForm):
    """Form for creating and editing reviews.

    Includes fields for headline, rating (1-5 stars), and body text.
    Uses custom radio buttons for rating and Bootstrap form controls.
    """
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