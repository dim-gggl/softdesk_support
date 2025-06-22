from rest_framework import serializers

from .models import User


class UserListSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for listing users.

    Returns:
    - id
    - username
    """

    class Meta:
        model = User
        fields = ["id", "username"]

class UserDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for user profiles.

    Handles:
    - Username and email uniqueness validation
    - Secure password hashing on creation
    - Optional email
    - Read-only fields: id, date_created
    """
    date_joined = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id", "username", "password", "email",
            "first_name", "last_name", "age",
            "can_be_contacted", "can_data_be_shared",
            "date_joined"
        ]

    def validate_username(self, value):
        """
        Ensures that the username is unique across all users.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value=None):
        """
        Validates that the email is either not provided, or unique 
        if provided.
        """
        if value:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    "If email is provided, it should "
                    "not be associated with another user"
                )
            return value
        else:
            return

    def create(self, validated_data):
        """
        Creates a new user instance with a hashed password.
        """
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
