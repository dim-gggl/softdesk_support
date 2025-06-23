from django.views.generic import RedirectView

from user.views import UserViewSet
from projects.views import (
    ProjectViewSet,
    ContributorViewSet,
    IssueViewSet,
    CommentViewSet,
)


class RootRedirectView(RedirectView):
    url = "api/"
