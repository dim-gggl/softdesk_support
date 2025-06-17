from django.contrib.auth import get_user_model

from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
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
        if self.action in ["update","partial_update","destroy"]:
            return [IsAuthenticated(), IsAuthor()]
        else:
            return [AllowAny()]

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(
            user=self.request.user,
            project=project
        )

    # @action(
    #         detail=False,
    #         methods=["get"],
    #         url_path="projects/<int:project_id>/contributors",
    #         permission_classes=[IsAuthenticated, IsContributor]
    # )
    # def get_contributors(self, pk=None):
    #     project = self.get_object()
    #     contributors = self.serializer_class.get_contributors(project)
    #     return Response(contributors, status=status.HTTP_200_OK)

    # @action(
    #     detail=True,
    #     methods=["post"],
    #     url_path="contributors",
    #     permission_classes=[IsAuthenticated, IsAuthor]
    # )
    # def add_contributor(self, request, pk=None):
    #     project = self.get_object()
    #     user_id = request.data.get("user_id")

    #     if not user_id:
    #         return Response(
    #             {"detail":
    #                 "User ID must be provided in the request body."
    #             },
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     try:
    #         User = settings.AUTH_USER_MODEL
    #         if isinstance(User, str):
    #             from django.apps import apps
    #             User = apps.get_model(User)
    #         new_user = get_object_or_404(User, id=user_id)
    #     except (ValueError, TypeError):
    #         return Response(
    #             {"detail": "Invalid User ID format."},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     if Contributor.objects.filter(
    #         project=project, user=new_user).exists():
    #         return Response(
    #             {"detail":
    #              "User is already a contributor to this project."
    #             },
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     Contributor.objects.create(project=project, user=new_user)
    #     serializer = ContributorSerializer(
    #         project.contributors.all(), many=True
    #     )
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    # @action(
    #         detail=True,
    #         methods=["get"],
    #         url_path="contributors/<int:contributor_id>/",
    #         permission_classes=[IsAuthenticated]
    # )
    # def retrieve_contributor(self, request, pk=None, contributor_id=None):
    #     project = self.get_object()
    #     contributor = get_object_or_404(Contributor, id=contributor_id)
    #     serializer = ContributorSerializer(contributor)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    # @action(
    #         detail=True,
    #         methods=["delete"],
    #         url_path="contributors/(?P<contributor_user_id>[^/.]+)",
    #         permission_classes=[IsAuthenticated, IsContributor]
    # )
    # def remove_contributor(self, request, pk=None, contributor_user_id=None):
    #     project = self.get_object()
    #     contributor = get_object_or_404(
    #         Contributor,
    #         project=project,
    #         user__id=contributor_user_id
    #     )

    #     self.check_object_permissions(request, contributor)

    #     contributor.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)

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
