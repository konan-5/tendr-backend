from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from tendr_backend.users.api.views import UserViewSet  # noqa

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

# router.register("users", UserViewSet)


urls = [
    path("landing/", include("tendr_backend.landing.urls")),
    path("waitlist/", include("tendr_backend.waitlist.urls")),
    path("users/", include("tendr_backend.users.api.urls")),
    path("apps/", include("tendr_backend.downloaded_tenders.urls")),
]

app_name = "api"

urlpatterns = urls
