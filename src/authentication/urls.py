from django.urls import path, include
from rest_framework import routers
from .views import UserModelViewSet

router = routers.SimpleRouter()
router.register("users", UserModelViewSet, basename="users")

urlpatterns = [
    path("api/", include(router.urls))
]
