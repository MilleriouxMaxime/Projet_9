from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models


class User(AbstractUser):
    """Custom user model for LITRevu."""
    
    bio = models.TextField(max_length=500, blank=True, verbose_name='Biographie')
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        null=True,
        blank=True,
        verbose_name='Photo de profil'
    )

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return self.username


class Ticket(models.Model):
    title = models.CharField(max_length=128, verbose_name='Titre')
    description = models.TextField(max_length=2048, blank=True, verbose_name='Description')
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name='Utilisateur')
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to='tickets/',
        verbose_name='Image')
    time_created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création')

    class Meta:
        ordering = ['-time_created']
        verbose_name = 'Billet'
        verbose_name_plural = 'Billets'

    def __str__(self):
        return f"{self.title}"


class Review(models.Model):
    ticket = models.ForeignKey(
        to=Ticket,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Billet')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name='Note')
    headline = models.CharField(
        max_length=128,
        verbose_name='Titre')
    body = models.TextField(
        max_length=8192,
        blank=True,
        verbose_name='Commentaire')
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Utilisateur')
    time_created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création')

    class Meta:
        ordering = ['-time_created']
        verbose_name = 'Critique'
        verbose_name_plural = 'Critiques'

    def __str__(self):
        return f"{self.headline}"


class UserFollows(models.Model):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Utilisateur')
    followed_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followed_by',
        verbose_name='Utilisateur suivi')
    time_created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création')

    class Meta:
        ordering = ['-time_created']
        verbose_name = 'Abonnement'
        verbose_name_plural = 'Abonnements'
        unique_together = ('user', 'followed_user',)
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F('followed_user')),
                name='cannot_follow_self'
            )
        ]

    def __str__(self):
        return f"{self.user} suit {self.followed_user}"
