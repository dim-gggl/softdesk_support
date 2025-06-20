from django.contrib.auth import get_user_model

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

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
        if self.action == "retrieve":
            return self.detail_serializer_class
        elif self.action == "create":
            return self.serializer_class
        else:
            return self.minimal_serializer


class AuthorModelMixin:
    """
    Mixin to centralize permission logic for views.

    - Always requires authenticated users.
    - Adds `IsAuthor` permission for update, partial_update, and 
    destroy actions.
    - Adds `IsContributor` permission for all other actions.
    """
    def get_permissions(self):
        perms = [IsAuthenticated()]
        if self.action in [
            "update", "partial_update", "destroy"
            ]:
            perms.append(IsAuthor())
        else:
            perms.append(IsContributor())
        return perms


class ProjectViewSet(
    DetailListMixin,
    AuthorModelMixin,
    ModelViewSet
    ):
    """
    ViewSet for managing Project objects.

    - Uses different serializers for list, detail, and 
    nested views.
    - Automatically creates a Contributor entry for the 
    author when a project is created.
    - Applies filtering on name, author username, type, 
    and id.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer
    minimal_serializer = ProjectMinimalSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = [
        "name",
        "author__username",
        "type",
        "id"
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



class ContributorViewSet(AuthorModelMixin, ModelViewSet):
    """
    ViewSet for managing Contributor objects.

    - Filters contributors by project_id.
    - Assigns project and user explicitly during creation 
    based on URL kwargs.
    """
    serializer_class = ContributorSerializer

    filterset_fields = [
        "is_author=True", "is_author=False",
        "username", "id",
    ]

    def get_queryset(self):
        return Contributor.objects.filter(
            project=self.kwargs["project_id"]
        )

    def perform_create(self, serializer):
        serializer.save(
            project_id=self.kwargs["project_id"],
            user_id=self.kwargs["user_id"]
        )


class IssueViewSet(
    DetailListMixin,
    AuthorModelMixin,
    ModelViewSet
    ):
    """
    ViewSet for managing Issue objects.

    - Uses context-aware serializers.
    - Filters issues by project_id.
    - Automatically assigns author and project 
    during creation.
    """
    serializer_class = IssueListSerializer
    detail_serializer_class = IssueDetailSerializer
    minimal_serializer = IssueMinimalSerializer
    filterset_fields = [
        "priority", "label", "status", "assignee_id",
        "is_finished", "to_do", "urgent",
    ]
    def get_queryset(self):
        return Issue.objects.filter(
            project_id=self.kwargs["project_id"]
        )

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            project_id=self.kwargs["project_id"]
        )


class CommentViewSet(
    DetailListMixin, AuthorModelMixin, ModelViewSet
    ):
    """
    ViewSet for managing Comment objects.

    - Uses context-aware serializers.
    - Filters comments by issue_pk.
    - Automatically assigns author and issue 
    during creation.
    """
    serializer_class = CommentDetailSerializer
    detail_serializer_class = CommentDetailSerializer
    minimal_serializer = CommentDetailSerializer

    def get_queryset(self):
        return Comment.objects.filter(
            issue_id=self.kwargs["issue_pk"],
        )

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            issue_id=self.kwargs["issue_pk"]
        )
