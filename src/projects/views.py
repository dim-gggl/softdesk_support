from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Project, Contributor
from .serializers import ProjectSerializer, ContributorSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Project.objects.all()
        params = self.request.query_params
        user = self.request.user

        project_name = params.get("name")
        if project_name:
            queryset = queryset.filter(name=project_name)

        author_username = params.get("author_username")
        if author_username:
            queryset = queryset.filter(author__username=author_username)

        project_type = params.get("type")
        if project_type:
            queryset = queryset.filter(type=project_type)

        project_id = params.get("id")
        if project_id:
            queryset = queryset.filter(id=project_id)

        return queryset

    def perform_create(self):
        serializer = self.serializer_class
        project = serializer.save(
            author=self.request.user
        )
        Contributor.objects.create(
            user=self.request.user, project=project
        )

    @action(detail=True, methods=["get"], url_path="contributors")
    def get_contributors(self):
        project = self.get_object()
        serializer = ContributorSerializer(
            project.contributors.all(), many=True
        )
        return Response(serializer.data, status=200)

    @action(detail=True, methods=["post", "get"], url_path="contributors")
    def add_contributor(self):
        project = self.get_object()
        if project.author != self.request.user:
            return Response({
                "detail":
                "Forbidden. Only the author can add contributors."
                }, status=403
            )
        user_id = self.request.data.get("user")
        new_user = get_object_or_404(
            settings.AUTH_USER_MODEL, id=user_id
        )
        if Contributor.objects.filter(
            project=project, user=new_user
            ).exists():
            return Response({
                "detail":
                "User already in contributors."
            }, status=400)
        Contributor.objects.create(
            project=project, user=new_user
        )
        serializer = ContributorSerializer(
            project.contributors.all(), many=True
        )
        return Response(serializer.data, status=201)
