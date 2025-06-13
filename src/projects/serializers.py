from rest_framework import serializers
from .models import Project, Contributor


class ProjectSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Project
        fields = [
            "id", "name",
            "description",
            "type", "author",
            "created_time"
        ]
        read_only_fields = [
            "id", "author",
            "created_time"
        ]


class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = [
            "id", "user",
            "project"
        ]
        read_only_fields = ["id"]
