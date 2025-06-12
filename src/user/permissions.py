from rest_framework import permissions

class IsAdminOrIsSelf(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action == "list":
            return request.user.is_authenticated

        if view.action == "register":
            return True

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True

        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        return obj == request.user
