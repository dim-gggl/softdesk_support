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
        fields = ["id", "project"]
        extra_kwargs = {
            "user": {"queryset": User.objects.all()}
        }
        read_only_fields = ["id"]


# class ContributorValidationMixin:
#     """
#     Base class for contributor validation mixins.
#     Ensures that only users who are valid contributors
#     (author, assignee, etc.) can be associated with
#     project-related objects such as issues or comments.

#     This mixin is designed to be used as a base class
#     for serializers that need to validate that users
#     involved in an action are contributors to the
#     project.

#     :param contributor_fields: List of fields that
#     should be validated as contributors (e.g., author,
#     assignee, contributors, etc)
#     """
#     contributor_fields = []

#     def validate(self, data):
#         """
#         Validates that the user involved in an action is a
#         contributor to the project.
#         """
#         validated_data = super().validate(data)

#         # Get the project from the context or data
#         project = self.context.get(
#             "project"
#         ) or validated_data["project"] or validated_data["issue"].project

#         # Iterate over the contributor fields and validate
#         # that the user is a contributor to the project
#         for field in self.contributor_fields:
#             user = validated_data.get(field)
#             if user and not user.contribution_links.filter(
#                 project=project
#             ).exists():
#                 raise ValidationError({
#                     field: (
#                         "This user is not a contributor to "
#                         "this project."
#                     )
#                 })
#         return validated_data


class CommentListSerializer(ModelSerializer):
    """
    Serializer for listing comments.
    Includes id, author, and content.
    """
    class Meta:
        model = Comment
        fields = [
            "id",
            "author",
            "content"
        ]

    def create(self, request, *args, **kwargs):
        """
        Overrides default creation logic to set the author
        from the request and assign the comment to the
        provided issue.
        """
        author = request.user
        issue = request.data.get("issue")
        comment = Comment(
            author=author,
            content=request.data["content"],
            issue=issue
        )
        comment.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED
        )

class CommentDetailSerializer(ModelSerializer):
    """
    Detailed serializer for comment objects.
    Includes contributor validation and read-only
    fields for author and issue.
    """
    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ["id"]


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
    This serializer is mostly used to 
    """
    comments_count = SerializerMethodField()

    class Meta:
        model = Issue
        fields = ISSUE_LIST_FIELDS + ["author"]


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
        queryset=User.objects.all()
    )
    comments_count = SerializerMethodField()

    class Meta:
        model = Issue
        fields = "__all__"
        read_only_fields = ["id", "author", "created_time"]


class IssueMinimalSerializer(
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
        serializer = IssueMinimalSerializer(queryset, many=True)
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
