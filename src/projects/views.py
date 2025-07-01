from django.contrib.auth import get_user_model

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator       
from .models import Project, Contributor, Issue, Comment
from .serializers import (
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectMinimalSerializer,
    ContributorSerializer,
    IssueDetailSerializer,
    IssueListSerializer,
    CommentSerializer,
)
from .permissions import (  
    IsAuthorOrIsAdmin, 
    IsContributor, 
    IsAssignee, 
    IsContributorOrIsAdmin,
    IsProjectAuthor
)
from .const import (
    PROJECT_ERROR_MESSAGE,
    ISSUE_ERROR_MESSAGE,
    COMMENT_ERROR_MESSAGE,
    CONTRIBUTOR_ERROR_MESSAGE,
    IS_AUTHOR_TRUE_MESSAGE,
    IS_AUTHOR_FALSE_MESSAGE,
    CONTRIBUTOR_UNAUTHORIZED_MESSAGE,
    CONTRIBUTOR_ALREADY_EXISTS_MESSAGE
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
        if self.action in [
            "retrieve", "create", "update", "partial_update",
        ]:
            return self.detail_serializer_class
        elif self.action == "list":
            return self.serializer_class
        else:
            return self.minimal_serializer


class AuthorModelMixin:
    """
    Mixin to centralize permission logic for views.

    - Always requires authenticated users.
    - Adds the `IsAuthorOrIsAdmin` permission for update 
    (`update`, `partial_update`) and delete (`destroy`) 
    actions.
    - Adds the `IsContributor` permission for all 
    other actions.
    """
    def get_permissions(self):
        perms = [IsAuthenticated, IsContributorOrIsAdmin]
        if self.action in [
            "update", "partial_update", "destroy"
        ]:
            perms.append(IsAuthorOrIsAdmin)
        return [perm() for perm in perms]


class ErrorResponseMixin(ModelViewSet):
    """
    Mixin to centralize error response handling logic for views.
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
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_create(serializer)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED
        )


class ProjectViewSet(
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

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        elif self.action in ["list", "retrieve"]:
            return [IsContributorOrIsAdmin()]
        else:
            return [IsAuthorOrIsAdmin()]

    # It redefines perform_create in order to make the
    # fact that when a Project is created, one contributor
    # is also, everytime : the Project's Author.
    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(
            user=self.request.user,
            project_id=project.id
        )

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(
            contributor_links__user=user
        )
        if self.action == 'retrieve':
            queryset = queryset.select_related(
                'author'
            ).prefetch_related(
                'contributor_links__user', 
                'issues__author', 
                'issues__assignee'
            )
        return queryset


class ContributorViewSet(
    ErrorResponseMixin,
    ModelViewSet
    ):
    """
    ViewSet for managing Contributor objects.

    - Filters contributors by project_id, user id and username.
    - Assigns project and user explicitly during creation
    based on URL kwargs.
    """
    permission_classes = [IsAuthenticated, IsContributor, IsAdminUser]
    serializer_class = ContributorSerializer

    error_message = CONTRIBUTOR_ERROR_MESSAGE

    filterset_fields = [
        "project_id", "user_id", "id", "user__username"
    ]

    def get_permissions(self):
        if self.action in ["list",]:
            return [IsContributor()]
        else:
            return [IsProjectAuthor()]
        
    def get_queryset(self):
        project_pk = self.kwargs.get("project_pk")
        queryset = Contributor.objects.filter(
            project_id=project_pk
        )

        queryset = queryset.select_related(
            'user', 'project__author'
        )

        is_author_param = self.request.query_params.get("is_author")
        if is_author_param is not None:
            try:
                # We already have project__author prefetched 
                # if queryset is not empty,
                # but to be safe and handle empty queryset, 
                # we fetch the project directly.
                project = Project.objects.select_related(
                    'author'
                ).get(pk=project_pk)
                queryset = queryset.filter(
                    user=project.author
                )
            except Project.DoesNotExist:
                return queryset.none()
        return queryset

    def perform_create(self, serializer):
        project_pk = self.kwargs["project_pk"]
        user_id = serializer.validated_data["user"].id
        if not Contributor.objects.filter(
            project_id=project_pk,
            user_id=user_id
        ).exists():
            serializer.save(
                project_id=project_pk,
                user_id=user_id
            )
        else:
            raise ValidationError(
                CONTRIBUTOR_ALREADY_EXISTS_MESSAGE
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
    minimal_serializer = IssueListSerializer
    error_message = ISSUE_ERROR_MESSAGE
    filterset_fields = [
        "priority", "label", "status", "assignee_id",
        "author_id", "id", "created_time", "project__id"
    ]

    def get_serializer_class(self):
        if self.action in [
            "create", "retrieve", "update", "partial_update"
        ]:
            return self.detail_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        queryset = Issue.objects.filter(
            project_id=self.kwargs["project_pk"]
        )
        if self.action in ['list', 'retrieve']:
            queryset = queryset.select_related(
                'author', 'assignee', 'project'
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            project=Project.objects.get(
                id=self.kwargs["project_pk"]
            )
        )

    def perform_update(self, serializer):
        super().perform_update(serializer)
        assignee = serializer.validated_data.get("assignee")
        serializer.save()


class CommentViewSet(
    AuthorModelMixin,
    ErrorResponseMixin,
    ModelViewSet
    ):
    """
    ViewSet for managing Comment objects.

    - Uses context-aware serializers.
    - Filters comments by issue_pk, author_id, id 
    and created_time.
    - Automatically assigns author and issue
    during creation.
    """
    serializer_class = CommentSerializer

    error_message = COMMENT_ERROR_MESSAGE

    filterset_fields = [
        "issue_id", "author_id", "id", "created_time"
    ]

    def get_queryset(self):
        queryset = Comment.objects.filter(
            issue_id=self.kwargs["issue_pk"],
        )
        if self.action in ['list', 'retrieve']:
            queryset = queryset.select_related(
                'author', 'issue__project', 'issue__author'
            )
        return queryset

    def perform_create(self, serializer):
        comment = serializer.save(  
            author=self.request.user,
            issue_id=self.kwargs["issue_pk"]
        )

    def destroy(self, request, *args, **kwargs):
        """
        Allows a user to delete their own comment.
        Checks that the authenticated user is the author of 
        the comment.
        """
        instance = self.get_object()
        
        if instance.author != request.user or not request.user.is_staff:
            return Response(
                {"detail": "You are not authorized to delete this comment."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        instance.delete()
        return Response(
            {"detail": "Comment deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )