from user.views import UserViewSet
from projects.views import (
    ProjectViewSet, ContributorViewSet, IssueViewSet, CommentViewSet
)
from django.views.generic import RedirectView


class RootRedirectView(RedirectView):
    url = "api/"
