from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import EmailValidator
from django.db.models import Sum
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework.reverse import reverse
from rest_framework_nested import serializers as nested_serializer

from awards.serializers import RedemptionSerializer, PatientProgramEnrollmentSerializer
from core.models import HIVClinic
from core.serializers import HIVClinicSerializer
from orders.models import DeliveryFeedBack
from users.models import (
    Profile, Doctor, Patient, DeliverAgent,
    USER_TYPE_CHOICES, GENDER_CHOICES, PatientNextOfKeen

)


class UserCredentialSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=16)
    password_confirm = serializers.CharField(max_length=16)

    def validate_password_confirm(self, value):
        password = self.initial_data.get('password')
        if password != value:
            raise serializers.ValidationError("The passwords must match")
        return value

    def validate_username(self, value):
        username = self.context.get('request').user.username
        if username != value:
            raise ValidationError("The passwords must match")
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data.get("password"))
        instance.save()
        return instance

    def create(self, validated_data):
        """
        When save is called it calls the create since no instance yet
        Here the create will call the update to change password
        :param validated_data:
        :return:
        """
        user = self.context.get('request').user
        self.update(user, validated_data)
        return user


class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=16)
    first_name = serializers.CharField(max_length=50, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    phone_number = PhoneNumberField()
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=16)
    confirm_password = serializers.CharField(max_length=16)

    def validate_username(self, value):
        try:
            User.objects.get(username=value)
        except ObjectDoesNotExist:
            return value
        raise serializers.ValidationError("User with that username already exist")

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except ObjectDoesNotExist:
            return value
        raise serializers.ValidationError("User with that Email already exist")

    def validate_confirm_password(self, value):
        password = self.initial_data.get('password')
        if password != value:
            raise serializers.ValidationError("The passwords must match")
        return value

    def update(self, instance, validated_data):
        """Just to avoid PEP warning"""
        return super().update(instance, validated_data)

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        phone = validated_data.pop("phone_number")
        user = User.objects.create_user(**validated_data)
        # UPDATE PROFILE THAT IS CREATED USING SIGNAL
        profile = user.profile
        profile.phone_number = phone
        profile.save()
        # CREATE USER TYPE OBJECT
        Patient.objects.create(
            user=user
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50, help_text="Enter username or Email")
    password = serializers.CharField(max_length=50)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ('url', 'gender', 'image', 'phone_number', 'address', 'user_type')
        extra_kwargs = {
            'user_type': {'read_only': True},
            'url': {'view_name': 'users:user-profile-detail'},
        }


class PublicProfileSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, instance):
        return instance.user.get_full_name()

    class Meta:
        model = Profile
        fields = ('name', 'image', 'phone_number')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="users:user-detail")
    name = serializers.SerializerMethodField()

    def get_name(self, instance):
        return instance.get_full_name()

    def validate_email(self, email):
        # validator = EmailValidator('Enter a valid email address.')
        # validator(email)
        if User.objects.filter(email=email).exclude(username=self.instance.username).exists():
            raise serializers.ValidationError('User With That Email Already Exists')
        return email

    class Meta:
        model = User
        fields = ['url', 'email', 'name', 'first_name', 'last_name']
        # extra_kwargs = {
        #     'first_name': {'write_only': True},
        #     'last_name': {'write_only': True},
        # }


class DoctorSerializer(serializers.ModelSerializer):
    hiv_clinic = serializers.HyperlinkedRelatedField(
        view_name='core:clinic-detail', queryset=HIVClinic.objects.all()
    )

    def to_representation(self, instance):
        _dict = super().to_representation(instance)
        base_clinic_url = _dict.pop("hiv_clinic")
        base_clinic_obj = {
            'hiv_clinic': HIVClinicSerializer(
                instance=instance.hiv_clinic,
                context=self.context
            ).data
        }
        _dict.update(base_clinic_obj)
        return _dict

    class Meta:
        model = Doctor
        fields = (
            'url',
            'doctor_number',
            'hiv_clinic',
            'created_at', 'updated_at')
        extra_kwargs = {
            'url': {'view_name': 'users:doctor-detail'},
            'doctor_number': {'read_only': True},
            'url': {'view_name': 'users:doctor-detail'},
            # 'hiv_clinic': {'view_name': 'core:clinic-detail'}

        }


class PatientNextOfKeenSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, instance):
        return reverse(
            viewname='users:next-of-keen-detail',
            args=[instance.patient.id, instance.id],
            request=self.context.get('request')
        )

    class Meta:
        model = PatientNextOfKeen
        fields = ('url', 'full_name', 'address', 'phone_number', 'created_at', 'updated_at')
        extra_kwargs = {
            'url': {'view_name': 'users:next-of-keen-detail'},
        }


class PatientSerializer(serializers.HyperlinkedModelSerializer):
    base_clinic = serializers.HyperlinkedRelatedField(
        view_name='core:clinic-detail', queryset=HIVClinic.objects.all()
    )
    next_of_keen = PatientNextOfKeenSerializer(many=True, read_only=True)
    loyalty_points = serializers.SerializerMethodField()
    enrollments = PatientProgramEnrollmentSerializer(many=True, read_only=True)

    # redemptions = serializers.SerializerMethodField()

    def get_loyalty_points(self, instance):
        return {
            'total': instance.total_points,
            'total_redeemed_points': instance.total_redemption_points,
            'redeem_count': instance.redemptions.all().count(),
            'redeemable_points': instance.points_balance,
            'points_url': reverse(
                viewname='users:patient-points',
                request=self.context.get('request'),
                args=[instance.id]
            ),
            'current_program_enrolment': PatientProgramEnrollmentSerializer(
                instance=instance.current_program_enrollment,
                context=self.context
            ).data,
            'redeem_url': reverse(
                viewname='users:patient-redeem-points',
                request=self.context.get('request'),
                args=[instance.id]
            ),
            'redeem_list': RedemptionSerializer(
                instance=instance.redemptions,
                many=True,
                context=self.context
            ).data
        }

    def to_representation(self, instance):
        _dict = super().to_representation(instance)
        nok = _dict.pop("next_of_keen")
        nok_obj = {
            'next_of_keen': {
                'count': len(nok),
                'url': reverse(
                    viewname='users:next-of-keen-list',
                    args=[instance.id],
                    request=self.context.get('request')
                ),
                'list': nok
            }
        }
        base_clinic_url = _dict.pop("base_clinic")
        base_clinic_obj = {
            'base_clinic': HIVClinicSerializer(
                instance=instance.base_clinic,
                context=self.context
            ).data
        }
        _dict.update(nok_obj)
        _dict.update(base_clinic_obj)
        return _dict

    class Meta:
        model = Patient
        fields = (
            'url',
            'patient_number', 'next_of_keen',
            'base_clinic',
            # 'redemptions',
            'enrollments',
            'loyalty_points',
            'created_at', 'updated_at'
        )
        extra_kwargs = {
            'url': {'view_name': 'users:patient-detail'},
            'patient_number': {'read_only': True},
            # 'base_clinic': {'view_name': 'core:clinic-detail'}
        }


class DeliverAgentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DeliverAgent
        fields = ('url', 'agent_number', 'delivery_mode',
                  'work_clinic',
                  'created_at', 'updated_at')
        extra_kwargs = {
            'url': {'view_name': 'users:agent-detail'},
            'agent_number': {'read_only': True},
            'delivery_mode': {'view_name': 'core:mode-detail'},
            'work_clinic': {'view_name': 'core:clinic-detail'}
        }

    def to_representation(self, instance):
        _dict = super().to_representation(instance)
        base_clinic_url = _dict.pop("work_clinic")
        base_clinic_obj = {
            'work_clinic': HIVClinicSerializer(
                instance=instance.work_clinic,
                context=self.context
            ).data
        }
        _dict.update(base_clinic_obj)
        return _dict


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    is_staff = serializers.BooleanField(read_only=True)
    profile = ProfileSerializer()
    agent = DeliverAgentSerializer(required=False)
    doctor = DoctorSerializer(required=False)
    patient = PatientSerializer(required=False)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'profile', 'patient', 'doctor', 'agent']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile")
        profile = Profile.objects.get_or_create(user=instance)[0]
        for key, value in profile_data.items():
            setattr(profile, key, value)
        profile.save()
        if profile.user_type == 'agent':
            agent = DeliverAgent.objects.get_or_create(user=instance)[0]
            agent_data = validated_data.pop('agent')
            for key, value in agent_data.items():
                setattr(agent, key, value)
            agent.save()
        elif profile.user_type == 'doctor':
            doctor = Doctor.objects.get_or_create(user=instance)[0]
            doctor_data = validated_data.pop('doctor')
            print(doctor_data)
            for key, value in doctor_data.items():
                setattr(doctor, key, value)
            doctor.save()
        else:
            patient = Patient.objects.get_or_create(user=instance)[0]
            patient_data = validated_data.pop('patient')
            for key, value in patient_data.items():
                setattr(patient, key, value)
            patient.save()
        return instance


class UserInformationViewSerializer(serializers.ModelSerializer):
    account_information = serializers.SerializerMethodField()
    profile_information = serializers.SerializerMethodField()
    user_type_information = serializers.SerializerMethodField()
    account_information_edit_url = serializers.SerializerMethodField()
    profile_information_edit_url = serializers.SerializerMethodField()
    user_type_information_edit_url = serializers.SerializerMethodField()

    # patient_next_of_keen_edit_url = serializers.SerializerMethodField()

    # def get_patient_next_of_keen_edit_urls(self, instance):
    #     if instance.profile.user_type == 'patient' and instance.profile.has_related_user_type:
    #         return reverse(
    #             viewname="users:patient-next-of-detail",
    #             args=[instance.patient.id],
    #             request=self.context.get('request')
    #         )

    def get_account_information_edit_url(self, instance):
        return reverse(
            viewname='users:user-detail',
            args=[instance.id],
            request=self.context.get('request')
        )

    def get_profile_information_edit_url(self, instance):
        return reverse(
            viewname='users:user-profile-detail',
            args=[instance.profile.id],
            request=self.context.get('request')
        )

    def get_user_type_information_edit_url(self, instance):
        if instance.profile.user_type == 'doctor' and instance.profile.has_related_user_type:
            return reverse(
                viewname="users:doctor-detail",
                args=[instance.doctor.id],
                request=self.context.get('request')
            )
        if instance.profile.user_type == 'agent' and instance.profile.has_related_user_type:
            return reverse(
                viewname="users:agent-detail",
                args=[instance.agent.id],
                request=self.context.get('request')
            )
        if instance.profile.user_type == 'patient' and instance.profile.has_related_user_type:
            return reverse(
                viewname="users:patient-detail",
                args=[instance.patient.id],
                request=self.context.get('request')
            )

    def get_account_information(self, instance):
        return UserSerializer(instance=instance, context=self.context).data

    def get_profile_information(self, instance):
        return ProfileSerializer(instance=instance.profile, context=self.context).data

    def get_user_type_information(self, instance):
        if instance.profile.user_type == 'patient' and instance.profile.has_related_user_type:
            return {
                instance.profile.user_type: PatientSerializer(
                    instance=instance.patient,
                    context=self.context
                ).data
            }
        if instance.profile.user_type == 'doctor' and instance.profile.has_related_user_type:
            return {
                instance.profile.user_type: DoctorSerializer(
                    instance=instance.doctor,
                    context=self.context
                ).data
            }
        if instance.profile.user_type == 'agent' and instance.profile.has_related_user_type:
            return {
                instance.profile.user_type: DeliverAgentSerializer(
                    instance=instance.agent,
                    context=self.context
                ).data
            }
        return {self.instance.profile.user_type: None}

    class Meta:
        model = User
        fields = (
            'account_information', 'profile_information',
            'user_type_information', 'account_information_edit_url',
            'profile_information_edit_url', 'user_type_information_edit_url',
            # 'patient_next_of_keen_edit_url'
        )
