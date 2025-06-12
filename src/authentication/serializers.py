from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField()
    date_created = serializers.ReadOnlyField()
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email",
            "first_name", "last_name", "age",
            "can_be_contacted", "can_data_be_shared",
            "date_created", "password"
        ]

