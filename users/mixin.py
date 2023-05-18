from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import BadRequest
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED
import requests
from awards.serializers import RedemptionSerializer, PatientProgramEnrollmentSerializer
from core import permisions as custom_permissions
from rest_framework import permissions, status
from urllib.parse import parse_qs
from users.models import Patient, AccountVerification
from users.serializers import (
    UserProfileSerializer, UserLoginSerializer,
    UserCredentialSerializer, UserRegistrationSerializer, UserInformationViewSerializer, ProfileSerializer,
    AccountSearchSerializer, AccountVerifySerializer
)
from users.utils import obscure_email, obscure_number, update_patient


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

    def is_valid(self, search, index):
        if not (search and index):
            raise BadRequest()
        try:
            index = int(index)
        except Exception as e:
            raise BadRequest()
        # check if exists
        response = requests.get(
            url=f"{settings.EMR_BASE_URL}users/patients/",
            params={'search': search}
        ).json()
        patients = list(filter(lambda _patient: _patient["id"] == index, response['results']))
        if not patients:
            raise BadRequest()
        patient = patients[0]
        return {
            'email': obscure_number(patient['email']),
            'phone_number': obscure_number(patient['phone_number'])
        }

    @action(
        methods=['post'], url_name='find-account', url_path='find-account', detail=False,
        serializer_class=AccountSearchSerializer, permission_classes=[
            permissions.IsAuthenticated, custom_permissions.IsPatient,
            custom_permissions.IsNotValidPatient], )
    def find_my_account(self, request, *args, **kwargs):
        """Find patient account with patient number or national id"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        params = serializer.data
        dict_ = serializer.validated_data
        results = []
        if not params:
            dict_['search'] = ""
            dict_["results"] = results
            return Response(
                data=dict_,
                status=status.HTTP_200_OK
            )
        response = requests.get(
            url=f"{settings.EMR_BASE_URL}users/patients/",
            params=params
        )
        patients = response.json()
        for patient in patients["results"]:
            obscured_number = obscure_number(patient['phone_number'])
            obscured_email = obscure_email(patient['email'])
            results.append({
                'email': obscured_email,
                'phone_number': obscured_number,
                'patient_number': patient['patient_number'],
                'request_verification_url': reverse(
                    viewname='users:user-request-verification',
                    request=request
                ) + f"?search={dict_['search']}&account={patient['id']}"
            })
        dict_['results'] = results
        return Response(data=dict_, status=status.HTTP_200_OK)

    @action(
        methods=['get'], url_name='request-verification', url_path='verify-request', detail=False,
        permission_classes=[permissions.IsAuthenticated, custom_permissions.IsPatient,
                            custom_permissions.IsNotValidPatient])
    def request_verification(self, request, *args, **kwargs):
        search = request.GET.get("search")
        index = request.GET.get("account")
        # validate query strong
        info = self.is_valid(search, index)
        # create verification object
        AccountVerification.objects.create(
            user=request.user,
            search_value=search,
            extra_data=str(index)
        )
        data = {
            'verify_url': reverse(
                viewname='users:user-verify',
                request=request
            ),
            'message': f"Check your email {info['email']} or phone number {info['phone_number']} for verification "
        }
        return Response(data=data)

    @action(
        methods=['post'], url_name='verify', url_path='verify', detail=False,
        serializer_class=AccountVerifySerializer,
        permission_classes=[permissions.IsAuthenticated, custom_permissions.IsPatient,
                            custom_permissions.IsNotValidPatient], )
    def account_verification(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data.get('code')
        try:
            verification = AccountVerification.objects.get(
                code=code,
                user=request.user,
                is_verified=False
            )
            response = requests.get(
                url=f"{settings.EMR_BASE_URL}users/patients/",
                params={'search': verification.search_value}
            ).json()
            index = int(verification.extra_data)
            patient = list(filter(lambda _patient: _patient["id"] == index, response["results"]))[0]
            update_patient(patient, request)
            verification.is_verified = True
            verification.save()
            return Response(data={"detail": "Account verification successful"}, status=status.HTTP_200_OK)
        except AccountVerification.DoesNotExist:
            return Response(data={"detail": "Account not found."}, status=status.HTTP_403_FORBIDDEN)


class DoctorNextOfKeenMixin:
    @action(detail=True)
    def next_of_keen(self, request, *args, **kwargs):
        pass
