from django.db import models
from django.contrib.auth.models import User


class CodeAnalysis(models.Model):

    BUG_RISK = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    project_name = models.CharField(
        max_length=150
    )

    python_file = models.FileField(
        upload_to="projects/"
    )

    bug_risk = models.CharField(
        max_length=20,
        choices=BUG_RISK,
        default="Low"
    )

    quality_score = models.IntegerField(
        default=0
    )

    security_score = models.IntegerField(
        default=0
    )

    health_score = models.IntegerField(
        default=0
    )

    ai_review = models.TextField(
        blank=True
    )

    refactoring = models.TextField(
        blank=True
    )

    learning_mode = models.TextField(
        blank=True
    )

    achievement = models.CharField(
        max_length=100,
        default="Beginner"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.project_name