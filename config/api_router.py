from django.urls import path, include
from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from tendr_backend.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)


urls = [
    path("landing/", include("tendr_backend.landing.urls")),
    path("waitlist/", include("tendr_backend.waitlist.urls")),
]

app_name = "api"

urlpatterns = router.urls + urls
