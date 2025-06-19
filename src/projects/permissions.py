from rest_framework.permissions import BasePermission

from .models import Contributor, Comment


class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsContributor(BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'project'):
            project = obj.project
        elif isinstance(obj, Comment):
            project = obj.issue.project
        else:
            project = obj
        # Même vérification côté objet
        return Contributor.objects.filter(
            project=project, user=request.user
        ).exists()


class IsAssignee(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.assignee
