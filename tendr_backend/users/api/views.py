import environ
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext as _
from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import BlacklistedToken, OutstandingToken, RefreshToken

from tendr_backend.scrape.models import Tender
from tendr_backend.users.api.serializers import MeSerializer, UserSerializer
from tendr_backend.waitlist.models import WaitDocument

User = get_user_model()
env = environ.Env()


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class RegisterUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            email = request.data["email"]
            password = request.data["password"]
            resource_id = request.data.get("resource_id")
            tendr = None
            if resource_id:
                try:
                    tendr = Tender.objects.get(resource_id=resource_id)
                except:  # noqa
                    tendr = None
            try:
                user = User.objects.get(email=email)
                if tendr:
                    WaitDocument.objects.create(user_id=user, tendr_id=tendr)
                return Response(
                    {"message": "already created"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                print(e)
                user = User.objects.create_user(email=email, password=password)
                if tendr:
                    WaitDocument.objects.create(user_id=user, tendr_id=tendr)

                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                verification_link = f"{env('FRONT_END_URL')}/mail-verify?uidb64={uidb64}&token={token}"
                # Send an email with the new verification link
                send_mail(
                    subject=_("Email Verification"),
                    message=_("Click the following link to verify your email: ") + verification_link,
                    from_email="info@tendr.bid",
                    recipient_list=[user.email],
                )

                return Response(
                    {
                        "message": "Email verification link sent successfully.",
                        "navigate": "/welcome",
                        "data": {
                            "user_info": MeSerializer(user).data,
                        },
                    },
                    status=status.HTTP_200_OK,
                )

        except Exception as e:
            print(e)
            return Response({"message": "Email and password fields are required"}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = User.objects.filter(email=email).first()
        serializer = MeSerializer(user)
        if user is None:
            return Response(
                {"message": "User does not exist.", "navigate": "/login"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.mail_verified:
            return Response(
                {"message": "Mail not verified.", "navigate": "/mail-verify"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.check_password(password):
            return Response(
                {"message": "Password is not correct.", "navigate": "/login"}, status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "success login.",
                "navigate": "/",
                "data": {
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "user_info": serializer.data,
                },
            }
        )


class FetchMe(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = MeSerializer(user)
        return Response(
            {
                # "message": "success login.",
                "navigate": "/",
                "data": {
                    "user_info": serializer.data,
                },
            }
        )


class SendMailVerifyView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = ()

    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()

        if user is None:
            return Response(
                {"message": "User does not exist.", "navigate": "/register"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user.mail_verified:
            return Response(
                {"message": "Your email is already verified.", "navigate": "/login"}, status=status.HTTP_200_OK
            )

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verification_link = f"{env('FRONT_END_URL')}/mail-verify?uidb64={uidb64}&token={token}"

        # Send an email with the new verification link
        send_mail(
            subject=_("Email Verification"),
            message=_("Click the following link to verify your email: ") + verification_link,
            from_email="sg.pythondev@gmail.com",
            recipient_list=[user.email],
        )

        return Response(
            {"message": "Email verification link resent successfully.", "data": {"user_info": {"email": email}}},
            status=status.HTTP_200_OK,
        )


class MailVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        uidb64 = request.data.get("uidb64")
        token = request.data.get("token")
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.mail_verified = True
                user.save()
                return Response(
                    {"message": "Email verified successfully.", "navigate": "/login"}, status=status.HTTP_200_OK
                )
            return Response(
                {"message": "Invalid verification link.", "navigate": "/mail-verify"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            print(e)
            return Response(
                {
                    "message": "Invalid verification link.",
                    "navigate": "/mail-verify",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        uidb64 = request.data.get("uidb64")
        token = request.data.get("token")
        password = request.data.get("password")
        confirm_password = request.data.get("confirmPassword")

        if password != confirm_password:
            return Response(
                {
                    "message": "password is not same.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.set_password(password)
                user.save()
                return Response(
                    {"message": "Reset Password successfully.", "navigate": "/login"}, status=status.HTTP_200_OK
                )
            return Response(
                {
                    "message": "Invalid verification link.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            print(e)
            return Response(
                {
                    "message": "Invalid verification link.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()

        if user:
            # Generate a reset password token and send a link to the user
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{env('FRONT_END_URL')}/reset-password?uidb64={uidb64}&token={token}"

            # Send an email with the reset password link
            send_mail(
                subject=_("Password Reset"),
                message=_("Click the following link to reset your password: ") + reset_link,
                from_email="sg.pythondev@gmail.com",
                recipient_list=[email],
            )

            return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)

        return Response({"message": "User with that email does not exist."}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response(
                    {"message": "Successfully logged out.", "navigate": "/login"}, status=status.HTTP_205_RESET_CONTENT
                )
            except Exception as e:
                print(e)
                return Response({"message": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"message": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)


class LogoutAllView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)

        return Response(
            {"message": "Successfully logged out all.", "navigate": "/login"}, status=status.HTTP_205_RESET_CONTENT
        )


class DeleteUserView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class RefreshTokenView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({"access_token": access_token})
        except Exception as e:
            print(e)
            return Response({"message": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
