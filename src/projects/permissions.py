from rest_framework import permissions


class IsAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsContributor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, "contributors"):
            if hasattr(obj, "project"):
                obj = obj.projet
            elif hasattr(obj, "issue"):
                obj = obj.issue.project
        return request.user in obj.contributors.all()


class IsAssignee(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.assignee
