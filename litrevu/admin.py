from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Ticket, Review, UserFollows

User = get_user_model()


class TicketAdmin(admin.ModelAdmin):
    """Admin configuration for the Ticket model.

    Customizes the admin interface with:
    - List display showing title, user, and creation time
    - Filters for time and user
    - Search functionality for title and description
    - Reverse chronological ordering
    """

    list_display = ("title", "user", "time_created")
    list_filter = ("time_created", "user")
    search_fields = ("title", "description")
    ordering = ("-time_created",)


class ReviewAdmin(admin.ModelAdmin):
    """Admin configuration for the Review model.

    Customizes the admin interface with:
    - List display showing headline, ticket, user, rating, and creation time
    - Filters for time, user, and rating
    - Search functionality for headline and body
    - Reverse chronological ordering
    """

    list_display = ("headline", "ticket", "user", "rating", "time_created")
    list_filter = ("time_created", "user", "rating")
    search_fields = ("headline", "body")
    ordering = ("-time_created",)


admin.site.register(User, UserAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(UserFollows)
