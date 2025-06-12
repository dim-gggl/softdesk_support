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
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        try:
            user = User.objects.create_user(**validated_data)
            return user
        except Exception as e:
            raise serializers.ValidationError({"Error": str(e)})

    def update(self, instance, validated_data):
        if "password" in validated_data:
            instance.set_password(validated_data["password"])
            validated_data.pop("password")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
