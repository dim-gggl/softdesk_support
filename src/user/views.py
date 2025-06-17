from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer
from .permissions import IsAdminOrIsSelf, IsSelf


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
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

        # if self.action == "create":
        #     permission_classes = [AllowAny]
        # elif self.action == "retrieve":
        #     permission_classes = [IsAuthenticated, IsAdminOrIsSelf]
        # elif self.action in ["update", "partial_update", "destroy"]:
        #     permission_classes = [IsAuthenticated, IsSelf]
        # elif self.action == "list":
        #     permission_classes = [IsAuthenticated]
        # else:
        #     permission_classes = [IsAuthenticated]
        # return [permission() for permission in permission_classes]

    def get_queryset(self):

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
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = [
            {"id": user["id"],
            "username": user["username"]}
            for user in serializer.data
        ]
        return Response(data)
