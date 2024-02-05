from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from tendr_backend.users.api.views import (
    DeleteUserView,
    FetchMe,
    ForgotPasswordView,
    GoogleAuthView,
    LoginView,
    LogoutView,
    MailVerifyView,
    RefreshTokenView,
    RegisterUserView,
    ResetPasswordView,
    SendMailVerifyView,
    UserViewSet,
)

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("", UserViewSet)

urlpatterns = [
    path("users/", include(router.urls)),
    path("sign-up/", RegisterUserView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("mail-verify/", MailVerifyView.as_view(), name="mail-verify"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("delete-user/<int:pk>/", DeleteUserView.as_view(), name="delete-user"),
    path("get-refresh-token/", RefreshTokenView.as_view(), name="get-refresh-token"),
    path("send-mail-verify/", SendMailVerifyView.as_view(), name="send-mail-verify"),
    path("fetch-me/", FetchMe.as_view(), name="fetch-me"),
    path("google/", GoogleAuthView.as_view(), name="googel-auth"),
]
