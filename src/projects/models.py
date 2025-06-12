from django.db import models
from django.conf import settings


class Project(models.Model):
    TYPES = ["back-end", "front-end", "ios", "android"]
    name = models.CharField(max_length=128)
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects"
    )
    type = models.CharField(
        max_length=20,
        choices=[
            (type.upper(), type) for type in TYPES
        ],
    )
    description = models.TextField(blank=True, null=True)
    created_time = models.DateTimeField(auto_now_add=True)


class Contributor(models.Model):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contributions"
    )
    project = models.ForeignKey(
        to=Project,
        on_delete=models.CASCADE,
        related_name="contributors"
    )
    class Meta:
        unique_together = ("user", "project")
