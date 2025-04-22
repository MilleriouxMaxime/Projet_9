"""Management command to generate sample data for testing the LITRevu application.

Generates:
- Test users with predefined usernames
- Follow relationships between users
- Sample book tickets with realistic French literature content
- Reviews on tickets with varied ratings and comments

All data is created with realistic timestamps to simulate actual usage.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from litrevu.models import Ticket, Review, UserFollows
from django.utils import timezone
import random
from datetime import timedelta

User = get_user_model()

SAMPLE_BOOKS = [
    {
        "title": "Le Petit Prince",
        "description": "Un classique de la littérature française qui raconte l'histoire d'un petit "
        "prince venant d'une autre planète. Une belle réflexion sur l'amitié et l'amour.",
    },
    {
        "title": "1984",
        "description": "Un roman dystopique fascinant qui dépeint une société sous surveillance "
        "constante. La vision de George Orwell reste étonnamment pertinente aujourd'hui.",
    },
    {
        "title": "Harry Potter à l'école des sorciers",
        "description": "Le premier tome de la célèbre série qui nous plonge dans un monde "
        "magique extraordinaire. Une histoire captivante pour petits et grands.",
    },
    {
        "title": "Les Misérables",
        "description": "L'œuvre magistrale de Victor Hugo qui suit le parcours de Jean "
        "Valjean. Une fresque sociale puissante sur la rédemption et la justice.",
    },
    {
        "title": "Le Comte de Monte-Cristo",
        "description": "Une histoire de vengeance et de rédemption captivante. "
        "Alexandre Dumas nous offre une aventure inoubliable pleine de rebondissements.",
    },
]

SAMPLE_REVIEWS = [
    {
        "headline": "Une lecture incontournable !",
        "body": "Ce livre m'a complètement transporté. L'écriture est fluide, les "
        "personnages sont attachants et l'histoire est prenante du début à la fin.",
        "rating": 5,
    },
    {
        "headline": "Bonne surprise",
        "body": "Je ne m'attendais pas à autant apprécier ce livre. L'intrigue "
        "est bien menée et les thèmes abordés sont très actuels.",
        "rating": 4,
    },
    {
        "headline": "Mitigé",
        "body": "Quelques passages sont vraiment excellents, mais l'ensemble manque "
        "parfois de rythme. Les personnages secondaires mériteraient plus de développement.",
        "rating": 3,
    },
    {
        "headline": "Un classique qui mérite sa réputation",
        "body": "Une œuvre majeure qui continue de résonner avec notre époque. La "
        "profondeur des personnages et la qualité de l'écriture sont remarquables.",
        "rating": 5,
    },
    {
        "headline": "Lecture agréable",
        "body": "Un bon moment de lecture, même si certains aspects de l'histoire sont "
        "prévisibles. Le style est agréable et l'univers bien construit.",
        "rating": 4,
    },
]


class Command(BaseCommand):
    """Django management command to populate the database with sample data.

    This command will:
    1. Clean existing non-superuser data
    2. Create test users (alice, bob, charlie, david)
    3. Create random follow relationships
    4. Create tickets for French literature books
    5. Generate reviews with varied ratings

    All created data uses realistic French content and timestamps.
    """

    help = "Generates sample data for testing"

    def handle(self, *args, **kwargs):
        """Execute the command to generate sample data.

        The data generation process follows these steps:
        1. Clean existing data (users, tickets, reviews, follows)
        2. Create test users with predefined usernames
        3. Create random follow relationships between users
        4. Create tickets for books with realistic timestamps
        5. Generate reviews for ~75% of tickets

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Outputs progress messages to stdout during execution.
        """
        # Clean existing data
        self.stdout.write("Cleaning existing data...")
        Review.objects.all().delete()
        Ticket.objects.all().delete()
        UserFollows.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        # Create test users
        self.stdout.write("Creating test users...")
        users = []
        usernames = ["alice", "bob", "charlie", "david"]
        for username in usernames:
            user = User.objects.create_user(
                username=username,
                password="password123",
                email=f"{username}@example.com",
            )
            users.append(user)

        # Create some follows
        self.stdout.write("Creating user follows...")
        for user in users:
            other_users = [u for u in users if u != user]
            # Follow 1-2 random users
            for followed_user in random.sample(other_users, random.randint(1, 2)):
                UserFollows.objects.create(user=user, followed_user=followed_user)

        # Create tickets and reviews
        self.stdout.write("Creating tickets and reviews...")
        for _ in range(8):  # Create 8 tickets
            user = random.choice(users)
            book = random.choice(SAMPLE_BOOKS)
            time_created = timezone.now() - timedelta(days=random.randint(20, 30))

            ticket = Ticket.objects.create(
                title=book["title"], description=book["description"], user=user
            )
            # Update time_created after creation
            Ticket.objects.filter(id=ticket.id).update(time_created=time_created)

            # 75% chance to have a review
            if random.random() < 0.75:
                # Review by a different user
                reviewer = random.choice([u for u in users if u != user])
                review_sample = random.choice(SAMPLE_REVIEWS)
                review = Review.objects.create(
                    ticket=ticket,
                    user=reviewer,
                    headline=review_sample["headline"],
                    body=review_sample["body"],
                    rating=review_sample["rating"],
                )
                # Update time_created after creation
                review_time = time_created - timedelta(days=random.randint(1, 7))
                Review.objects.filter(id=review.id).update(time_created=review_time)

        self.stdout.write(self.style.SUCCESS("Successfully generated sample data"))
