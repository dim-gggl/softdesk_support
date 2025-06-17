from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Project, Contributor, Issue, Comment
from user.serializers import UserSerializer


User = get_user_model()

class ContributorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Contributor
        fields = [
            "id", "user",
            "project"
        ]
        read_only_fields = ["id"]


class ContributorValidationMixin:
    contributor_fields = []

    def validate(self, data):
        data = super().validate(data)
        project = self.context.get("project") or data["project"]
        for field in self.contributor_fields:
            user = data.get(field)
            if user and not user.contributions.filter(project=project).exists():
                raise serializers.ValidationError({
                    field: (
                        "This user is not a contributor to "
                        "this project."
                    )
                })
        return data

class IssueSerializer(
    ContributorValidationMixin,
    serializers.ModelSerializer
    ):
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    contributor_fields = ["author", "assignee"]

    class Meta:
        model = Issue
        fields = [
            "id", "title",
            "description",
            "project",
            "assignee"
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

class CommentSerializer(
    ContributorValidationMixin,
    serializers.ModelSerializer
):
    contributor_fields = ["author"]

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ["id", "author", "created_time", "issue"]



class ProjectListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = [
            "id", "name", "type"
        ]

    def validate_name(self, value):
        if Project.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                "Project with this name already exists"
            )
        return value


class ProjectDetailSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    contributors = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "name",
            "description",
            "type", "author",
            "created_time",
            "contributors"
        ]
        read_only_fields = [
            "id", "author",
            "created_time"
        ]

    def get_contributors(self, instance):
        queryset = instance.contributors.all()
        serializer = ContributorSerializer(queryset, many=True)
        return serializer.data


