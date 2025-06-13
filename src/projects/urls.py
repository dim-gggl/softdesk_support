from django.urls import path, include
from rest_framework import routers
from .views import ProjectViewSet

router = routers.SimpleRouter()
router.register(r"projects", ProjectViewSet, basename="project")

urlpatterns = [
    path("", include(router.urls))
]
