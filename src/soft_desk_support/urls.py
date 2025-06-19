from django.contrib import admin
from django.urls import path, include

from .views import RootRedirectView

import api_urls


urlpatterns = [
    path("", RootRedirectView.as_view()),
    path('admin/', admin.site.urls),
    path('api/', include(api_urls)),
]
