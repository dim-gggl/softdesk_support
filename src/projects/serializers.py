"""
Serializers for the projects app.

Since, in this repository, most of the objects are nested,
the serializers are quite complex.

They are organized in the following way:

    - The Mixins which are used to add shared logic to the 
    serializers.
    (e.g in order to centralize the permissions logic)

    - The List Serializers which are used to list the objects.
    (e.g when the user wants the list of projects, issues, comments, 
    etc.)

    - The Detail Serializers which are used to retrieve or create 
    the objects.
    (e.g when the user wants the details of a project, issue, comment, 
    etc.)

    - The Minimal Serializers which are used to list the objects
    in a minimal way when they are nested in a listed object.
    (e.g when the user wants the details of a project, he won't see
    all the issues listed in the project but will get the Minimal Serializer
    of the issues)
"""

from django.contrib.auth import get_user_model

from rest_framework.serializers import (
    PrimaryKeyRelatedField,
    ValidationError,
    ModelSerializer,
    SerializerMethodField,
    StringRelatedField,
    IntegerField
)

from rest_framework.validators import UniqueTogetherValidator

from .models import Project, Contributor, Issue, Comment
from .const import ISSUE_LIST_FIELDS

User = get_user_model()


class ContributorSerializer(ModelSerializer):
    """
    Serializer for the Contributor model.
    Handles serialization of project contributor data.
    """

    class Meta:
        model = Contributor
        fields = ["id", "user", "project"]
        read_only_fields = ["id", "project"]

    def validate(self, attrs):
        project_id = self.context["view"].kwargs.get("project_pk")
        user = attrs.get("user")
        if Contributor.objects.filter(
            user=user, 
            project_id=project_id
        ).exists():
            raise ValidationError(
                "This user is already contributing "
                "to the project"
            )
        return attrs


class CommentSerializer(ModelSerializer):
    """
    Detailed serializer for comment objects.
    Includes contributor validation and read-only
    fields for author and issue.
    """
    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ["id", "author", "issue"]


class IssueSerializerMixin:
    """
    Mixin for issue serializers, providing shared logic such
    as comment count.
    """
    comments_count = SerializerMethodField()

    def get_comments_count(self, instance):
        return instance.comments.count()


class IssueListSerializer(
    IssueSerializerMixin,
    ModelSerializer
    ):
    """
    Minimal serializer for issues.
    Returns only issue ID, author ID, and comment count.
    """
    issue_id = IntegerField(source="id", read_only=True)
    author_id = IntegerField(read_only=True)
    comments_count = SerializerMethodField()

    class Meta:
        model = Issue
        fields = [
            "issue_id",
            "author_id",
            "comments_count"
        ]
        extra_kwargs = {
            "assignee": {
                "required": False,
                "allow_null": True
            }
        }
        read_only_fields = [
            "author_id", 
            "comments_count",
        ]


class IssueDetailSerializer(
    IssueSerializerMixin,
    ModelSerializer
    ):
    """
    Detailed serializer for issues with contributor
    validation.
    Includes logic for setting the author on creation.
    """
    assignee = PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    comments_count = SerializerMethodField()

    class Meta:
        model = Issue
        fields = [
            "title", "label", "priority", "status",
            "created_time", "comments_count", "assignee"
        ]
        extra_kwargs = {
            "assignee": {
                "required": False,
                "allow_null": True
            }
        }
        read_only_fields = [
            "id", 
            "author", 
            "created_time", 
            "comments_count"
        ]


class ProjectListSerializer(ModelSerializer):
    """
    Serializer for listing basic project details.
    """

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "type",
            "description"
        ]

    def validate_name(self, value):
        """
        Validates that the project name is unique.
        """
        if Project.objects.filter(name=value).exists():
            raise ValidationError(
                "Project with this name already exists"
            )
        return value


class ProjectDetailSerializer(ModelSerializer):
    """
    Detailed serializer for projects.
    Includes contributors and associated issues.
    """
    author = StringRelatedField(read_only=True)
    contributors = SerializerMethodField()
    issues = SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "type",
            "author",
            "created_time",
            "contributors",
            "issues"
        ]
        read_only_fields = [
            "id",
            "author",
            "created_time"
        ]

    def get_contributors(self, instance):
        """
        Returns serialized data for all contributors linked
        to the project.
        """
        queryset = instance.contributor_links.all()
        serializer = ContributorSerializer(queryset, many=True)
        return serializer.data

    def get_issues(self, instance):
        """
        Returns minimal serialized data for all issues linked
        to the project.
        """
        queryset = instance.issues.all()
        serializer = IssueListSerializer(queryset, many=True)
        return serializer.data


class ProjectMinimalSerializer(ModelSerializer):
    """
    Minimal serializer for project representation.
    Includes project ID and author ID.
    """
    project_id = IntegerField(source="id", read_only=True)
    author_id = IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = [
            "project_id",
            "author_id"
        ]
