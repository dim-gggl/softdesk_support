import uuid

from django.db import models
from django.conf import settings


class TimeStampedModel(models.Model):
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)ss"
    )
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Project(TimeStampedModel):
    TYPES = ["back-end", "front-end", "ios", "android"]
    name = models.CharField(max_length=128)
    type = models.CharField(
        max_length=20,
        choices=[
            (type.upper(), type) for type in TYPES
        ],
    )
    description = models.TextField(blank=True, null=True)


class Contributor(models.Model):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contributions",
    )
    project = models.ForeignKey(
        to=Project,
        on_delete=models.CASCADE,
        related_name="contributors"
    )
    class Meta:
        unique_together = ("user", "project")

    def is_author(self):
        return self.user_id == self.project.author_id


class Issue(TimeStampedModel):
    PRIORITIES = [
        ("low","LOW"),
        ("medium","MEDIUM"),
        ("high","HIGH")
    ]
    LABELS = [
        ("bug","BUG"),
        ("feature","FEATURE"),
        ("task","TASK")
    ]
    STATUSES = [
        ("todo","TODO"),
        ("in_progress","IN_PROGRESS"),
        ("finished","FINISHED")
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    project = models.ForeignKey(
        to=Project,
        on_delete=models.CASCADE,
        related_name="issues"
    )
    priority = models.CharField(max_length=10, choices=PRIORITIES)
    label = models.CharField(max_length=10, choices=LABELS)
    status = models.CharField(
        max_length=15,
        choices=STATUSES,
        default="todo"
    )
    assignee = models.ForeignKey(
        to=Contributor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_issues"
    )


class Comment(TimeStampedModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    issue = models.ForeignKey(
        to=Issue,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    content = models.TextField()
