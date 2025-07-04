from rest_framework.permissions import BasePermission

from .models import Contributor, Comment, Issue


class IsAuthorOrIsAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Comment):
            return obj.author == request.user or request.user.is_staff
        elif hasattr(obj, "author"):
            return obj.author == request.user or request.user.is_staff
        else:
            return request.user.is_staff


class IsContributor(BasePermission):
    def has_permission(self, request, view):
       return Contributor.objects.filter(
            user__id=request.user.id
        ).exists()
    
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


class IsContributorOrIsAdmin(IsContributor):
    def has_permission(self, request, view):
        return super().has_permission(
            request, view
        ) or request.user.is_staff
    
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(
            request, view, obj
        ) or request.user.is_staff


class IsProjectAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        project = obj.project
        return project.author == request.user


class IsAssignee(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, Issue):
            print(
                "Did you try to assign a user to a non-issue object?"
            )
            return False
        return request.user == obj.assignee
