from django.apps import AppConfig


class LitrevuConfig(AppConfig):
    """Configuration class for the LITRevu application.

    Defines basic Django application settings including the app name
    and database auto field type.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'litrevu'
