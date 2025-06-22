from django.urls import include, path

from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

from soft_desk_support.views import (
    UserViewSet,
    ProjectViewSet,
    ContributorViewSet,
    IssueViewSet,
    CommentViewSet,
)


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r"projects", ProjectViewSet)

projects_router = NestedSimpleRouter(
    router, r"projects", lookup="project"
)
projects_router.register(
    r"contributors",
    ContributorViewSet,
    basename="project_contributors"
)
projects_router.register(
    r"issues", IssueViewSet, basename="project_issues"
)

issues_router = NestedSimpleRouter(
    projects_router, r"issues", lookup="issue"
)
issues_router.register(
    r"comments", CommentViewSet, basename="issue_comments"
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(projects_router.urls)),
    path('', include(issues_router.urls)),
]
