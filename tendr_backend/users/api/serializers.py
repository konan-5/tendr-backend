from django.contrib.auth import get_user_model
from rest_framework import serializers

from tendr_backend.users.models import User as UserType

User = get_user_model()


class UserSerializer(serializers.ModelSerializer[UserType]):
    class Meta:
        model = User
        fields = ["name", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
        }


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "role",
            "mail_verified",
            "phone_number",
            "address",
            "avatar_image",
            "company",
            "birthday",
            "date_joined",
            "last_login",
        ]


class OtherUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "avatar",
        ]
