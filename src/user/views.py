from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import User
from .serializers import UserDetailSerializer
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
        Returns a list of users with only their id and username exposed.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = [
            {"id": user["id"],
            "username": user["username"]}
            for user in serializer.data
        ]
        return Response(data)
