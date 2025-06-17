from rest_framework import permissions

class IsAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

class IsContributor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.contributors.all()

class IsAssignee(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.assignee
