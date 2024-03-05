import environ
import requests
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

from tendr_backend.common.utils.helper import send_email_smtp  # noqa
from tendr_backend.users.api.serializers import MeSerializer, UserSerializer

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
        print(request.data)
        email = request.data.get("email")
        password = request.data.get("password")
        name = request.data.get("name")  # Make sure this matches the frontend field name

        # Check if a user with the provided email already exists
        if User.objects.filter(email=email).exists():
            return Response({"type": "email", "message": "Already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new user
        user = User.objects.create_user(email=email, name=name, password=password)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        # Generate email verification token
        # Send verification email
        # send_mail(
        #     subject="Verify your email address",
        #     message=f"Please click the following link to verify your email address: {verification_link}",
        #     from_email=env('EMAIL_HOST_USER'),
        #     recipient_list=[email],
        # )
        verification_link = f"'hello'/auth/mail-verify?uidb64={uidb64}&token={token}"
        print(verification_link)

        return Response(
            {
                "message": "Registered successfully. Please check your email to verify your account.",
                "navigate": "/confirmation-required",
                "verification_link": verification_link,
                # "data": {
                #     "user_info": MeSerializer(user).data,
                # },
            },
            status=status.HTTP_201_CREATED,
        )

        # try:
        #     email = request.data["email"]
        #     password = request.data["password"]
        #     resource_id = request.data.get("resource_id")
        #     name = request.data["fullName"]
        #     tendr = None
        #     if resource_id:
        #         try:
        #             tendr = Tender.objects.get(resource_id=resource_id)
        #         except:  # noqa
        #             tendr = None
        #     try:
        #         user = User.objects.get(email=email)
        #         if tendr:
        #             WaitDocument.objects.create(user_id=user, tendr_id=tendr)
        #         return Response(
        #             {"message": "Already created"},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     except Exception as e:
        #         print(e)
        #         user = User.objects.create_user(email=email, name=name, password=password)
        #         if tendr:
        #             WaitDocument.objects.create(user_id=user, tendr_id=tendr)

        #         uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        #         token = default_token_generator.make_token(user)
        #         verification_link = f"efefew/auth/mail-verify?uidb64={uidb64}&token={token}"  # noqa
        #         # verification_link = f"{env('FRONT_END_URL')}/auth/mail-verify?uidb64={uidb64}&token={token}"  # noqa
        #         # Send an email with the new verification link
        #         # send_mail(
        #         #     subject=_("Email Verification"),
        #         #     message=_("Click the following link to verify your email: ") + verification_link,
        #         #     from_email="info@tendr.bid",
        #         #     recipient_list=[user.email],
        #         # )

        #         # email_content = f"Full Name: {full_name}\n" f"Email: {email}\n"
        #         # send_email_smtp("New Waiter", email_content, "ikedahiroshi517@gmail.com")
        #         print(verification_link)
        #         # send_email_smtp("Mail Verify", verification_link, email)

        #         return Response(
        #             {
        #                 "message": "Registered successfully",
        #                 "navigate": "/auth/welcome",
        #                 "verification":verification_link
        #                 # "data": {
        #                 #     "user_info": MeSerializer(user).data,
        #                 # },
        #             },
        #             status=status.HTTP_200_OK,
        #         )

        # except Exception as e:
        #     print(e)
        #     return Response(
        #         {"message": "Email and password, fullname fields are required"}, status=status.HTTP_400_BAD_REQUEST
        #     )


class SignInView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = User.objects.filter(email=email).first()
        serializer = MeSerializer(user)
        print(serializer.data)
        if user is None:
            return Response(
                {"type": "email", "message": "User does not exist."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not user.check_password(password):
            return Response(
                {"type": "password", "message": "Password is not correct."}, status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.mail_verified:
            return Response({"navigate": "/confirmation-required"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "success login.",
                # "navigate": "/",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                # "user": serializer.data
                "user": {
                    "role": "admin",
                    "data": {
                        "name": serializer.data["name"],
                        "photoURL": "assets/images/avatars/brian-hughes.jpg",
                        "email": serializer.data["email"],
                        "settings": {"layout": {}, "theme": {}},
                        "shortcuts": ["apps.calendar", "apps.mailbox", "apps.contacts"],
                    },
                },
            }
        )


class AccessToken(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = MeSerializer(user)
        print(serializer.data)
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                # "message": "success login.",
                # "user": serializer.data,
                "user": {
                    "role": "admin",
                    "data": {
                        "name": serializer.data["name"],
                        "photoURL": "assets/images/avatars/brian-hughes.jpg",
                        "email": serializer.data["email"],
                        "settings": {"layout": {}, "theme": {}},
                        "shortcuts": ["apps.calendar", "apps.mailbox", "apps.contacts"],
                    },
                },
                "access_token": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
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
        print(request.data)
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


class GoogleAuthView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": request.data["code"],
            "client_id": env("GOOGLE_CLIENT_ID"),
            "client_secret": env("GOOGLE_CLIENT_SECRET"),
            "redirect_uri": env("GOOGLE_REDIRECT_URI"),
            "grant_type": "authorization_code",
        }
        response = requests.post(token_url, data=data)

        print(response)

        return Response("data")
