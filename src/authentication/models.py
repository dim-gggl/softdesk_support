from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxLengthValidator, MaxValueValidator


class CustomUserManager(UserManager):
    """
    Custom user manager that handles the age field for superuser creation.
    """
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        if "age" not in extra_fields:
            extra_fields["age"] = 25
        return super().create_superuser(username, email, password, **extra_fields)

class User(AbstractUser, PermissionsMixin):
    """
    Represents a user of SoftDesk Support.

    Requirements:
    - Must be at least 15 years old.
    - Must provide a unique username, password, and email address
    (for account recovery).
    - First and last names are optional.
    - Can choose to allow contact and data sharing with third parties.
    - Account creation date is automatically recorded.
    """
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(15), MaxValueValidator(99)],
        help_text="User must be at least 15 years old."
    )
    password = models.CharField(max_length=128)
    username = models.CharField(
        validators=[MaxLengthValidator(100)],
        unique=True,
        help_text="Unique username for the user."
    )
    first_name = models.CharField(
        max_length=30,
        blank=True,
        validators=[MaxLengthValidator(30)]
    )
    last_name = models.CharField(
        max_length=30,
        blank=True,
        validators=[MaxLengthValidator(30)]
    )
    can_be_contacted = models.BooleanField(
        default=True,
        help_text="Allow SoftDesk to contact you about your projects.",
        verbose_name="Do you accept receiving emails from SoftDesk Support ?"
    )
    can_data_be_shared = models.BooleanField(
        default=True,
        help_text="Allow your data to be shared with third parties.",
        verbose_name=(
            "Do you accept SoftDesk Support to share your data with "
            "third parties ?"
        )
    )
    date_created = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(
        null=True,
        help_text="Unique email address for the user.",
        blank=True
    )

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        return self

    # def is_contributor(self, project: Project) -> bool:
    #     """
    #     Check if the user is a contributor to the given project.
    #     Args:
    #         project (Project): The project to check.
    #     Returns:
    #         bool: True if the user is a contributor, False otherwise.
    #     """
    #     if isinstance(project, Project):
    #         return self.id in project.contributors.values_list(
    #             "user__id", flat=True
    #         )
    #     return False

    # def is_author(self, post: Project | Comment) -> bool:
    #     """
    #     Check if the user is the author of the given project or comment.

    #     Args:
    #         post (Project | Comment): The project or comment to check.

    #     Returns:
    #         bool: True if the user is the author, False otherwise.
    #     """
    #     if isinstance(post, Project):
    #         return self.id == post.author.id
    #     elif isinstance(post, Comment):
    #         return self.id == post.author.id
    #     return False

    # def is_assigned(self, issue: Issue) -> bool:
    #     """
    #     Check if the user is assigned to the given issue.

    #     Args:
    #         issue (Issue): The issue to check.

    #     Returns:
    #         bool: True if the user is assigned, False otherwise.
    #     """
    #     if isinstance(issue, Issue):
    #         return self.id in issue.assignees.values_list(
    #             "id", flat=True
    #         )
    #     return False

    def __str__(self):
        return self.username

    def __repr__(self):
        return f"<User id={self.id}>"

    class Meta:
        ordering = ["-date_joined"]
        verbose_name = "user"
        verbose_name_plural = "users"

