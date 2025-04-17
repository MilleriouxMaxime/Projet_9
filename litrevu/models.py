from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO
from django.core.files import File


class User(AbstractUser):
    """Custom user model for LITRevu."""
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
        verbose_name='Image',
        help_text='Image maximum size is 800x800 pixels')
    time_created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création')

    class Meta:
        ordering = ['-time_created']
        verbose_name = 'Billet'
        verbose_name_plural = 'Billets'

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        if self.image:
            # Open image
            img = Image.open(self.image)
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Set maximum size
            max_size = (400, 400)
            
            # Resize if larger than maximum size while maintaining aspect ratio
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
            # Save the processed image
            output = BytesIO()
            img.save(output, format='JPEG', quality=85)
            output.seek(0)
            
            # Replace the image field with processed image
            self.image = File(output, name=self.image.name)
        
        super().save(*args, **kwargs)


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


class UserBlocks(models.Model):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blocking',
        verbose_name='Utilisateur')
    blocked_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blocked_by',
        verbose_name='Utilisateur bloqué')
    time_created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création')

    class Meta:
        ordering = ['-time_created']
        verbose_name = 'Blocage'
        verbose_name_plural = 'Blocages'
        unique_together = ('user', 'blocked_user',)
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F('blocked_user')),
                name='cannot_block_self'
            )
        ]

    def __str__(self):
        return f"{self.user} a bloqué {self.blocked_user}"


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

    def clean(self):
        # Check if the user is blocked by the followed_user
        if UserBlocks.objects.filter(user=self.followed_user, blocked_user=self.user).exists():
            raise ValidationError("Vous ne pouvez pas suivre un utilisateur qui vous a bloqué.")
        # Check if the user has blocked the followed_user
        if UserBlocks.objects.filter(user=self.user, blocked_user=self.followed_user).exists():
            raise ValidationError("Vous ne pouvez pas suivre un utilisateur que vous avez bloqué.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} suit {self.followed_user}"
