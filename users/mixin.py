from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED

from awards.serializers import RedemptionSerializer
from core import permisions as custom_permissions
from rest_framework import permissions

from users.models import Patient
from users.serializers import (
    UserProfileSerializer, UserLoginSerializer,
    UserCredentialSerializer, UserRegistrationSerializer, UserInformationViewSerializer, ProfileSerializer
)


class DoctorsMixin:
    @action(detail=False, url_name='doctor-list', url_path='doctors')
    def doctors_list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(profile__user_type='doctor')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PatientsMixin:
    @action(
        detail=False, url_name='patient-list', url_path='patients',
        permission_classes=[custom_permissions.IsAgentOrDoctor]
    )
    def patients_list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(profile__user_type='patient')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AgentsMixin:
    @action(detail=False, url_name='agent-list', url_path='agents')
    def agents_list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(profile__user_type='agent')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, url_name='agent-detail', permission_classes=[permissions.IsAuthenticated])
    def agent_detail(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class AuthMixin:

    @action(
        methods=['post'],
        url_path='change-password',
        url_name='change_password',
        description="Change current User password",
        detail=True,
        permission_classes=[
            permissions.IsAuthenticated
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
        serializer_class=UserRegistrationSerializer,
        permission_classes=[
            permissions.AllowAny
        ],
    )
    def register(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            data = UserInformationViewSerializer(instance=user, context={'request': request}).data
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
        serializer_class=UserLoginSerializer,
        permission_classes=[
            permissions.AllowAny
        ],
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
            data = UserInformationViewSerializer(instance=user, context={'request': request}).data
            data.update({'token': token.key})
            return Response(data)


class ProfileMixin:
    @action(
        methods=['put', 'get'],
        description='User profile',
        detail=False,
        permission_classes=[
            permissions.IsAuthenticated
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
        methods=['put', 'get'],
        description='User profile',
        detail=True,
        permission_classes=[
            permissions.IsAuthenticated
        ],
        serializer_class=ProfileSerializer
    )
    def profile_detail(self, request, *args, **kwargs):
        user = request.user.profile
        serializer = self.get_serializer(data=request.data, instance=user)
        if request.method == 'PUT':
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
        return Response(self.get_serializer(instance=user).data)

    @action(
        methods=['get'],
        description='User profile view',
        detail=False,
        permission_classes=[
            permissions.IsAuthenticated
        ],
        url_name='profile-view',
        url_path='profile-view',
        serializer_class=UserInformationViewSerializer)
    def profile_view(self, request, *args, **kwargs):
        user = request.user
        return Response(self.get_serializer(instance=user).data)


class LoyaltyPointsMixin:
    @action(
        permission_classes=[
            permissions.IsAuthenticated,
            custom_permissions.IsPatient
        ],
        methods=['get'],
        url_path='points',
        url_name='points',
        detail=True
    )
    def points(self, request, *args, **kwargs):
        patient = get_object_or_404(Patient, id=kwargs['pk'])
        data = {
            'total': patient.total_points,
            'total_redeemed_points': patient.total_redemption_points,
            'redeem_count': patient.redemptions.all().count(),
            'points': patient.points_balance,
            'redemption': RedemptionSerializer(
                instance=patient.redemptions.all(),
                many=True,
                context={'request': request}
            ).data
        }
        return Response(data)

    @action(
        permission_classes=[
            permissions.IsAuthenticated,
            custom_permissions.IsPatient
        ],
        methods=['post'],
        url_path='redeem-points',
        url_name='redeem-points',
        detail=True,
        serializer_class=RedemptionSerializer
    )
    def redeem(self, request, *args, **kwargs):
        patient = get_object_or_404(Patient, id=kwargs['pk'], user=request.user)
        serializer = RedemptionSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # TODO CHECK IF MAX REDEMPTION REACHED IN EITHER SERIALIZER validator or here
        points_redeemed = serializer.validated_data.get("reward").point_value
        instance = serializer.save(patient=patient, points_redeemed=points_redeemed)
        data = {
            'total': patient.total_points,
            'total_redeemed_points': patient.total_redemption_points,
            'redeem_count': patient.redemptions.all().count(),
            'points': patient.points_balance,
            'redemption': RedemptionSerializer(instance=instance, context={'request': request}).data
        }
        return Response(data)
