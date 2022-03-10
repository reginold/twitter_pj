from crypt import methods

from accounts.api.serializers import LoginSerializer, SignupSerializer, UserSerializer
from django.contrib.auth import authenticate as django_authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import User
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class AccountViewSet(viewsets.ViewSet):
    """
    API endpoint that identify the user status.
    """

    serializer_class = SignupSerializer

    @action(methods=["GET"], detail=False)
    def login_status(self, request):
        """
        API endpoint that identify the user status.
        """
        data = {"has_logged_in": request.user.is_authenticated}
        if request.user.is_authenticated:
            data["user"] = UserSerializer(request.user).data
        return Response(data)

    @action(methods=["POST"], detail=False)
    def logout(self, request):
        """
        API endpoint that logout the user.
        """
        django_logout(request)
        return Response({"has_logged_out": True})

    @action(methods=["POST"], detail=False)
    def login(self, request):
        """
        API endpoint that login the user.
        """

        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Please check input",
                    "errors": serializer.errors,
                },
                status=400,
            )
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        if not User.objects.filter(username=username).exists():
            return Response(
                {
                    "success": False,
                    "message": "User not found",
                    "errors": {"username": ["User not found"]},
                },
                status=400,
            )
        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response(
                {
                    "success": False,
                    "message": "username and password does not match",
                },
                status=400,
            )
        django_login(request, user)
        return Response(
            {
                "success": True,
                "user": UserSerializer(instance=user).data,
            }
        )

    @action(methods=["POST"], detail=False)
    def signup(self, request):
        """
        API endpoint that signup the user.
        """
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Please check input",
                    "errors": serializer.errors,
                },
                status=400,
            )

        user = serializer.save()
        django_login(request, user)
        return Response(
            {
                "success": True,
                "user": UserSerializer(user).data,
            },
            status=201,
        )
