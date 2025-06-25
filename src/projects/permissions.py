from rest_framework.permissions import BasePermission

from .models import Contributor, Comment, Issue


class IsAuthorOrIsAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, "author"):
            obj = obj.project
        return obj.author == request.user or request.user.is_staff


class IsContributor(BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'project'):
            project = obj.project
        elif isinstance(obj, Comment):
            project = obj.issue.project
        else:
            project = obj
        return Contributor.objects.filter(
            project_id=project.id, user_id=request.user.id
        ).exists()


class IsAssignee(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, Issue):
            print(
                "Did you try to assign a user to a non-issue object?"
            )
            return False
        return request.user == obj.assignee
