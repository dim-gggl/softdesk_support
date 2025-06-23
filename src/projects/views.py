from django.contrib.auth import get_user_model

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from .models import Project, Contributor, Issue, Comment
from .serializers import (
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectMinimalSerializer,
    ContributorSerializer,
    IssueDetailSerializer,
    IssueListSerializer,
    IssueMinimalSerializer,
    CommentDetailSerializer,
)
from .permissions import IsAuthor, IsContributor
from .const import (
    PROJECT_ERROR_MESSAGE,
    ISSUE_ERROR_MESSAGE,
    COMMENT_ERROR_MESSAGE,
    CONTRIBUTOR_ERROR_MESSAGE
)

User = get_user_model()


class DetailListMixin(ModelViewSet):
    """
    Mixin class to determine which serializer to use depending
    on the view context.

    - `serializer_class`: used for list and create actions.
    - `detail_serializer_class`: used for retrieve action.
    - `minimal_serializer`: used for nested or non-detailed
        contexts (e.g., when included in another serializer).

    This abstraction helps reduce boilerplate code in viewsets
    with multiple serializer needs.
    """
    serializer_class = ""
    detail_serializer_class = ""
    minimal_serializer = ""

    def get_serializer_class(self):
        if self.action in ["retrieve", "create", "update", "partial_update"]:
            return self.detail_serializer_class
        elif self.action == "list":
            return self.serializer_class
        else:
            return self.minimal_serializer


class AuthorModelMixin:
    """
    Mixin to centralize permission logic for views.

    - Always requires authenticated users.
    - Adds the `IsAuthor` permission for update 
    (`update`, `partial_update`) and delete (`destroy`) 
    actions.
    - Adds the `IsContributor` permission for all 
    other actions.
    """
    def get_permissions(self):
        perms = [IsAuthenticated, IsContributor]
        if self.action in [
            "update", "partial_update", "destroy"
        ]:
            perms.append(IsAuthor)
        return [perm() for perm in perms]


class ErrorResponseMixin(ModelViewSet):
    """
    Mixin to centralize error response handling logic for views.
    Inherits from `AuthorModelMixin` to add permissions.
    Then overrides the `create` method to handle error responses 
    in case of POST requests on lists views without request body.

    Provides the template request the user should send to create
    a new object.
    """
    error_message = ""

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, 
            context=self.get_serializer_context()
        )

        if not serializer.is_valid():
            return Response(
                self.error_message,
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_create(serializer)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED
        )


class ProjectViewSet(
    AuthorModelMixin,
    DetailListMixin,
    ErrorResponseMixin,
    ModelViewSet
    ):
    """
    ViewSet for managing Project objects.

    - Uses different serializers for list, detail, and
    nested views.
    - Automatically creates a Contributor entry for the
    author when a project is created.
    - Applies filtering on name, author username, type,
    created_time and id.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer
    minimal_serializer = ProjectMinimalSerializer
    error_message = PROJECT_ERROR_MESSAGE
    filterset_fields = [
        "name", "author__username", "type", "id",
        "created_time", "author__id"
    ]

    # It redefines perform_create in order to make the
    # fact that when a Project is created, one contributor
    # is also, everytime : the Project's Author.
    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(
            user=self.request.user,
            project=project
        )

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(
            contributor_links__user=user
        )


class ContributorViewSet(
    AuthorModelMixin,
    ErrorResponseMixin,
    ModelViewSet
    ):
    """
    ViewSet for managing Contributor objects.

    - Filters contributors by project_id, user id and username.
    - Assigns project and user explicitly during creation
    based on URL kwargs.
    """
    serializer_class = ContributorSerializer

    filterset_fields = [
        "project_id", "user_id", "id", "user__username"
    ]

    def get_queryset(self):
        return Contributor.objects.filter(
            project=self.kwargs["project_pk"]
        )

    def perform_create(self, serializer):
        serializer.save(
            project_id=self.kwargs["project_pk"],
            user_id=self.kwargs["user_pk"]
        )


class IssueViewSet(
    AuthorModelMixin,
    DetailListMixin,
    ErrorResponseMixin,
    ModelViewSet
    ):
    """
    ViewSet for managing Issue objects.

    - Uses context-aware serializers.
    - Filters issues by priority, label, status, assignee_id,
    author_id, created_time and project_id.
    - Automatically assigns author and project
    during creation.
    """
    serializer_class = IssueListSerializer
    detail_serializer_class = IssueDetailSerializer
    minimal_serializer = IssueMinimalSerializer
    error_message = ISSUE_ERROR_MESSAGE
    filterset_fields = [
        "priority", "label", "status", "assignee_id",
        "author_id", "id", "created_time", "project__id"
    ]

    def get_queryset(self):
        return Issue.objects.filter(
            project_id=self.kwargs["project_pk"]
        )

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            project_id=self.kwargs["project_pk"]
        )


class CommentViewSet(
    AuthorModelMixin,
    DetailListMixin, 
    ErrorResponseMixin,
    ModelViewSet
    ):
    """
    ViewSet for managing Comment objects.

    - Uses context-aware serializers.
    - Filters comments by issue_pk, author_id, id and created_time.
    - Automatically assigns author and issue
    during creation.
    """
    serializer_class = CommentDetailSerializer
    detail_serializer_class = CommentDetailSerializer
    minimal_serializer = CommentDetailSerializer

    error_message = COMMENT_ERROR_MESSAGE

    filterset_fields = [
        "issue_id", "author_id", "id", "created_time"
    ]

    def get_queryset(self):
        return Comment.objects.filter(
            issue_id=self.kwargs["issue_pk"],
        )

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            issue_id=self.kwargs["issue_pk"]
        )
