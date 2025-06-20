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
        fields = ["id","project"]
        extra_kwargs = {
            "user": {"queryset": User.objects.all()}
        }
        read_only_fields = ["id"]


class ContributorValidationMixin:
    """
    Mixin to validate that users involved in an action are 
    contributors to the project.
    Ensures that only users who are valid contributors 
    (author, assignee, etc.)
    can be associated with project-related objects such 
    as issues or comments.
    """
    contributor_fields = []

    def validate(self, data):
        data = super().validate(data)
        project = self.context.get(
            "project"
        ) or data["project"] or data["issue"].project
        for field in self.contributor_fields:
            user = data.get(field)
            if user and not user.contribution_links.filter(
                project=project
            ).exists():
                raise ValidationError({
                    field: (
                        "This user is not a contributor to "
                        "this project."
                    )
                })
        return data


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


    def create(self, validated_data):
        """
        Overrides default creation logic to set the author 
        from the request
        and assign the comment to the provided issue.
        """
        self.fields = [
            "id", "content",
            "author", "issue"
        ]
        author = self.request.user
        issue = self.context.get(
            "issue"
        ) or validated_data["issue"]
        comment = Comment(
            author=author,
            content=validated_data["content"],
            issue=issue
        )
        comment.save()
        return comment


class CommentDetailSerializer(
    ContributorValidationMixin,
    ModelSerializer
    ):
    """
    Detailed serializer for comment objects.
    Includes contributor validation and read-only 
    fields for author and issue.
    """
    contributor_fields = ["author"]

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = [
            "id",
            "author",
            "created_time",
            "issue"
        ]


class CommentMinimalSerializer(ModelSerializer):
    """
    Minimal representation of a comment.
    Returns only comment ID and author ID.
    """
    comment_id = IntegerField(
        source="id", read_only=True
    )
    author_id = IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = ["comment_id", "author_id"]


class IssueSerializerMixin(ModelSerializer):
    """
    Mixin for issue serializers, providing shared logic such 
    as comment count.
    """
    comments_count = SerializerMethodField()

    class Meta:
        model = Issue
        fields = ISSUE_LIST_FIELDS

    def get_comments_count(self, instance):
        """
        Returns the number of comments linked to this 
        issue instance.
        """
        return instance.comments.count()


class IssueListSerializer(
    IssueSerializerMixin,
    ModelSerializer
    ):
    """
    Serializer for listing issues.
    Includes comment count and author.
    """
    comments_count = SerializerMethodField()

    class Meta:
        model = Issue
        fields = ISSUE_LIST_FIELDS + ["author"]


class IssueDetailSerializer(
    IssueSerializerMixin,
    ContributorValidationMixin,
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
    contributor_fields = ["author", "assignee"]

    class Meta:
        model = Issue
        fields = "__all__"
        read_only_fields = ["id"]

    def create(self, validated_data):
        """
        Sets the request user as the author when creating 
        a new issue.
        """
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class IssueMinimalSerializer(IssueSerializerMixin, ModelSerializer):
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