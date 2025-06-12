from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import UserSerializer
from .permissions import IsAdminOrIsSelf


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "create":
                permission_classes = [AllowAny]
        elif self.action in ["retrieve", "update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, IsAdminOrIsSelf]
        elif self.action == "list":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

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


    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = [
            {"id": user["id"],
            "username": user["username"]}
            for user in serializer.data
        ]
        return Response(data)

    @action(methods=["post"], detail=False, permission_classes=[AllowAny],
            url_path="register", url_name="user_register")
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

    # @action(methods=["patch"], detail=True, permission_classes=[IsAdminOrIsSelf],
    #         url_path=f"{user_id}/update/", url_name="update-user")
    # def update(self, request):
    #     data = request.data
    #     if isinstance(data, dict):
    #         user = get_object_or_404(id=data["id"])
    #         for k, v in data.items():
    #             if hasattr(user, k):
    #                 user.__setattr__(v)
    #     elif isinstance(data, list):




