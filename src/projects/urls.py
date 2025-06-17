from rest_framework_nested import routers
from .views import (
    ProjectViewSet, ContributorViewSet,
    IssueViewSet, CommentViewSet
)

router = routers.SimpleRouter()
router.register(r"projects", ProjectViewSet)

projects_router = routers.NestedSimpleRouter(
    router, r"projects", lookup="project"
)
projects_router.register(
    r"contributors",
    ContributorViewSet,
    basename="project-contributors"
)
projects_router.register(
    r"issues", IssueViewSet, basename="project-issues"
)

issues_router = routers.NestedSimpleRouter(
    projects_router, r"issues", lookup="issue"
)
issues_router.register(
    r"comments", CommentViewSet, basename="issue-comments"
)

urlpatterns = router.urls + projects_router.urls + issues_router.urls
