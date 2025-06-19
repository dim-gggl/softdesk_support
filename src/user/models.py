from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MinValueValidator, MaxLengthValidator


class CustomUserManager(UserManager):
    """
    Custom user manager that ensures the `age` field is populated when creating a superuser.
    Sets a default age of 25 if not provided.
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
    Custom User model extending Django's AbstractUser for SoftDesk Support.

    Fields:
    - age: Required integer >= 15 (default for superuser: 25)
    - username: Unique, max 100 characters
    - email: Optional but must be unique
    - first_name, last_name: Optional fields with respective max lengths
    - can_be_contacted: Opt-in for SoftDesk communications
    - can_data_be_shared: Opt-in for third-party data sharing
    - date_created: Auto-generated when account is created

    Meta:
    - Orders users by newest (`-date_joined`)
    """
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(15), MaxLengthValidator(99)],
        help_text="min. 15-years-old."
    )
    username = models.CharField(
        validators=[MaxLengthValidator(100)],
        unique=True,
        help_text="Unique username (will be visible by other users)"
    )
    first_name = models.CharField(
        max_length=30,
        blank=True,
        validators=[MaxLengthValidator(30)]
    )
    last_name = models.CharField(
        max_length=40,
        blank=True,
        validators=[MaxLengthValidator(40)]
    )
    can_be_contacted = models.BooleanField(
        default=False,
        help_text=(
            "Allow SoftDesk to send you emails to keep you"
            " updated about their products"
        )
    )
    can_data_be_shared = models.BooleanField(
        default=False,
        help_text=(
            "Allow SoftDesk to share your information with third parties"
            " in order to customize your experience."
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
        """
        Overrides save to allow future extensions; currently just calls parent method.
        """
        super(User, self).save(*args, **kwargs)
        return self

    def __str__(self):
        """
        Returns the username as the string representation.
        """
        return self.username

    def __repr__(self):
        """
        Returns a debug-friendly string with user ID.
        """
        return f"<User id={self.id}>"

    class Meta:
        ordering = ["-date_joined"]
        verbose_name = "user"
        verbose_name_plural = "users"
