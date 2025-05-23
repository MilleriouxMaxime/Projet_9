# Generated by Django 5.0.2 on 2025-04-16 10:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("litrevu", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserBlocks",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "time_created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Date de création"
                    ),
                ),
                (
                    "blocked_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="blocked_by",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Utilisateur bloqué",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="blocking",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Utilisateur",
                    ),
                ),
            ],
            options={
                "verbose_name": "Blocage",
                "verbose_name_plural": "Blocages",
                "ordering": ["-time_created"],
            },
        ),
        migrations.AddConstraint(
            model_name="userblocks",
            constraint=models.CheckConstraint(
                check=models.Q(("user", models.F("blocked_user")), _negated=True),
                name="cannot_block_self",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="userblocks",
            unique_together={("user", "blocked_user")},
        ),
    ]
