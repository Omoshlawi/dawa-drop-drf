from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED

from users.serializers import (
    UserSerializer, UserCredentialSerializer,
    UserRegistrationSerializer, UserLoginSerializer,
    UserProfileSerializer
)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        methods=['post'],
        url_path='change-password',
        url_name='change_password',
        description="Change current User password",
        detail=True,
        permission_classes=[
            IsAuthenticated
        ],
        serializer_class=UserCredentialSerializer
    )
    def change_password(self, request, *args, **kwargs):
        """
        Simply works as view function on view methods
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = UserCredentialSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'changed': True})

    @action(
        methods=['post'],
        description="Supports user registration system",
        detail=False,
        url_name='register',
        url_path='register',
        serializer_class=UserRegistrationSerializer
    )
    def register(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            data = UserProfileSerializer(instance=user, context={'request': request}).data
            data.update({'token': token.key})
            return Response(
                data,
                status=HTTP_201_CREATED
            )

    @action(
        methods=['post'],
        description='User Login View',
        detail=False,
        url_path='login',
        url_name='login',
        serializer_class=UserLoginSerializer
    )
    def login(self, request, *args, **kwargs):
        _serializers = UserLoginSerializer(data=request.data)
        if _serializers.is_valid(raise_exception=True):
            username = _serializers.validated_data.get("username")
            password = _serializers.validated_data.get("password")
            user = authenticate(
                username=username,
                password=password
            )
            if not user:
                return Response({
                    'username': [''],
                    'password': ['Invalid Username or password'],
                },
                    status=400)
            token, created = Token.objects.get_or_create(user=user)
            data = UserProfileSerializer(instance=user, context={'request': request}).data
            data.update({'token': token.key})
            return Response(data)

    @action(
        methods=['put', 'get'],
        description='User profile',
        detail=False,
        permission_classes=[
            IsAuthenticated
        ],
        # authentication_classes=[TokenAuthentication, BasicAuthentication],
        serializer_class=UserProfileSerializer
    )
    def profile(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data, instance=user)
        if request.method == 'PUT':
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
        return Response(self.get_serializer(instance=user).data)

    @action(
        methods=['get'],
        detail=False,
        authentication_classes=[TokenAuthentication],
        permission_classes=[
            IsAuthenticated
        ],
        description="Get user by token",
        url_path='get-user-by-token'
    )
    def get_user_by_token(self, request, *args, **kwargs):
        user = request.user
        return Response(self.get_serializer(instance=user).data)
