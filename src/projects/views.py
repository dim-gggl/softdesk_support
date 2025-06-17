from django.contrib.auth import get_user_model

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import viewsets

from .models import Project, Contributor, Issue, Comment
from .serializers import (
    ProjectDetailSerializer,
    ProjectListSerializer,
    ContributorSerializer,
    IssueSerializer,
    CommentSerializer
)
from .permissions import IsAuthor, IsContributor


User = get_user_model()


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer

    filterset_fields = ["name", "author__username", "type", "id"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return self.detail_serializer_class
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAuthor()]
        else:
            return [IsAuthenticated()]

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(
            user=self.request.user,
            project=project
        )


class ContributorViewSet(viewsets.ModelViewSet):
    serializer_class = ContributorSerializer

    def get_queryset(self):
        return Contributor.objects.filter(project=self.kwargs["project_pk"])

    def get_permissions(self):
        match self.action:
            case "create":
                return [IsAuthenticated(), IsAuthor()]
            case "destroy":
                return [IsAuthenticated(), IsAuthor()] or [IsAdminUser()]
            case "list" | "retrieve":
                return [IsAuthenticated(), IsContributor()]
            case _:
                return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(project_id=self.kwargs["project_pk"])


class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer

    def get_queryset(self):
        return Issue.objects.filter(project_id=self.kwargs["project_pk"])

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            project_id=self.kwargs["project_pk"]
        )

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsContributor()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAuthor()]
        else:
            return [IsAuthenticated()]


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(
            issue_id=self.kwargs["issue_pk"],
            issue__project_pk=self.kwargs["project_pk"]
        )

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            issue_id=self.kwargs["issue_pk"]
        )

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsContributor()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAuthor()]
        else:
            return [IsAuthenticated()]
