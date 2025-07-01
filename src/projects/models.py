import uuid

from django.db import models
from django.contrib.auth import get_user_model

from .const import (
    ISSUE_LABELS as LABELS,
    ISSUE_PRIORITIES as PRIORITIES,
    ISSUE_STATUSES as STATUSES,
    PROJECT_TYPES as TYPES,
)


User = get_user_model()


class TimeStampedModel(models.Model):
    """
    Abstract base model that adds `author` and `created_time` fields
    to any model that inherits from it.
    """
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="%(class)ss"
    )
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Project(TimeStampedModel, models.Model):
    """
    Project model representing a software development project.

    Attributes:
    - name: name of the project
    - type: one of back-end, front-end, ios, or android
    - description: optional text description of the project
    - author and created_time: inherited from TimeStampedModel
    """
    name = models.CharField(max_length=128)
    type = models.CharField(
        max_length=20,
        choices=[
            (t, t.lower()) for t in TYPES
        ],
    )
    description = models.TextField(blank=True, null=True)


class Contributor(models.Model):
    """
    Intermediate model linking users and projects to represent
    contributors.

    Each pair (user, project) must be unique.

    Methods:
    - is_author(): returns True if the contributor is the project
    author
    """
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="contribution_links",
    )

    project = models.ForeignKey(
        to=Project,
        on_delete=models.CASCADE,
        related_name="contributor_links"
    )

    class Meta:
        unique_together = ("user", "project")

    def is_author(self):
        return self.user.id == self.project.author.id


class Issue(TimeStampedModel, models.Model):
    """
    Issue model representing a task, bug, or feature within
    a project.

    Attributes:
    - title, description: basic information
    - priority: LOW, MEDIUM, or HIGH
    - label: BUG, FEATURE, or TASK
    - status: TODO, IN_PROGRESS, or FINISHED
    - assignee: optional user responsible for the issue
    - project: the related project
    - author and created_time: inherited from TimeStampedModel
    """

    title = models.CharField(max_length=255)
    description = models.TextField(
        blank=True,
        null=True
    )
    project = models.ForeignKey(
        to=Project,
        on_delete=models.CASCADE,
        related_name="issues"
    )
    priority = models.CharField(
        max_length=10,
        choices=[
            (p, p.lower()) for p in PRIORITIES
        ]
    )
    label = models.CharField(
        max_length=10,
        choices=[
            (l, l.lower()) for l in LABELS
        ]
    )
    status = models.CharField(
        max_length=15,
        choices=[
            (stat, stat.lower()) for stat in STATUSES
            ],
        default="TODO"
    )
    assignee = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_issues"
    )


class Comment(TimeStampedModel, models.Model):
    """
    Comment model representing a comment left on an issue.

    Attributes:
    - id: UUID primary key
    - content: the comment text (max 250 chars)
    - issue: related issue
    - author and created_time: inherited from TimeStampedModel
    """
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
    content = models.TextField(max_length=250)

    class Meta:
        ordering = ["-created_time"]
