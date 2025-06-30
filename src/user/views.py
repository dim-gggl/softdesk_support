from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import User
from .serializers import UserDetailSerializer, UserListSerializer
from .permissions import IsAdminOrIsSelf, IsSelf


class UserViewSet(ModelViewSet):
    """
    ViewSet for managing user accounts.

    Permissions:
    - Anyone can create a new user
    - Only the user themselves (or admin) can retrieve their profile
    - Only the user can update or delete their account
    - Authenticated users can list users with filtered search

    Filtering:
    - ?username=
    - ?id=
    - ?contact_ok=true|false
    - ?data_shared_ok=true|false
    """
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer

    def get_serializer_class(self):
            if self.action == 'list':
                return UserListSerializer
            return UserDetailSerializer

    def get_permissions(self):
        """
        Returns appropriate permissions based on the action:
        - create: open to anyone
        - retrieve: requires user to be authenticated and either the
        user or admin
        - update, partial_update, destroy: only the user themselves
        - other actions: authenticated users only
        """
        match self.action:
            case "create":
                permission_classes = [AllowAny]
            case "retrieve":
                permission_classes = [IsAuthenticated, IsAdminOrIsSelf]
            case "update" | "partial_update" | "destroy":
                permission_classes = [IsAuthenticated, IsSelf]
            case _:
                permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Returns the filtered queryset of users based on query parameters:
        - username
        - id
        - contact_ok
        - data_shared_ok
        """
        queryset = User.objects.all()
        params = self.request.query_params

        user_username = params.get("username")
        if user_username:
            queryset = queryset.filter(username=user_username)

        user_id = params.get("id")
        if user_id:
            queryset = queryset.filter(id=user_id)

        contact_ok = params.get("contact_ok")
        if contact_ok:
            queryset = queryset.filter(
                can_be_contacted=contact_ok.lower() == "true"
            )

        data_shared_ok = params.get("data_shared_ok")
        if data_shared_ok:
            queryset = queryset.filter(
                can_data_be_shared=data_shared_ok.lower() == "true"
            )
        return queryset

    def list(self, request, *args, **kwargs):
        """
        Returns a list of users using UserListSerializer.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Allows a user to delete their own profile.
        Checks that the authenticated user is the owner of the profile.
        """
        instance = self.get_object()
        
        if instance != request.user:
            return Response(
                {"detail": "You are not authorized to delete this profile."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        instance.delete()
        return Response(
            {"detail": "Profile deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
