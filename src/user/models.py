from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MinValueValidator, MaxLengthValidator
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):
    """
    Custom user manager that handles the age field for superuser creation.
    """
    def create_superuser(
            self, username, email=None,
            password=None, **extra_fields
    ):
        if "age" not in extra_fields:
            extra_fields["age"] = 25
        return super().create_superuser(
            username, email, password,
            **extra_fields
        )


class User(AbstractUser):
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
        validators=[MinValueValidator(15)],
        help_text="Must be at least 15 years old."
    )
    password = models.CharField(max_length=50)
    username = models.CharField(
        validators=[MaxLengthValidator(100)],
        unique=True,
        help_text="Unique username to display"
    )
    first_name = models.CharField(
        max_length=30,
        blank=True,
        validators=[MaxLengthValidator(30)]
    )
    last_name = models.CharField(
        max_length=30,
        blank=True,
        validators=[MaxLengthValidator(40)]
    )
    can_be_contacted = models.BooleanField(
        default=False,
        help_text="Allow SoftDesk to contact you about your projects.",
    )
    can_data_be_shared = models.BooleanField(
        default=False,
        help_text="Allow your data to be shared with third parties.",
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

    def __str__(self):
        return self.username

    def __repr__(self):
        return f"<User id={self.id}>"

    class Meta:
        ordering = ["-date_joined"]
        verbose_name = "user"
        verbose_name_plural = "users"
