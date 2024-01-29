from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField, EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from tendr_backend.users.managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for Tendr.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = EmailField(_("email address"), unique=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True, null=True)
    mail_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=1024, blank=True, null=True)
    avatar = models.ImageField(blank=True, null=True, upload_to="users/avatar")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})
