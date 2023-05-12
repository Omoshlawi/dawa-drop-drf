from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from agents.models import DeliverAgent
from agents.serializers import DeliverAgentSerializer
from core.models import HealthFacility
from core.serializers import HealthFacilitySerializer
from doctors.serializers import DoctorSerializer
from patients.models import PatientNextOfKeen, Patient
from patients.serializers import PatientSerializer
from users.models import Profile, Doctor


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

    def validate_username(self, username):
        # validator = EmailValidator('Enter a valid email address.')
        # validator(email)
        if User.objects.filter(username=username).exclude(username=self.instance.username).exists():
            raise serializers.ValidationError('User With That Username Already Exists')
        return username

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'name', 'first_name', 'last_name']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': False},
            'username': {'required': False},
        }


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
                viewname="doctors:doctor-detail",
                args=[instance.doctor.id],
                request=self.context.get('request')
            )
        if instance.profile.user_type == 'agent' and instance.profile.has_related_user_type:
            return reverse(
                viewname="agents:agent-detail",
                args=[instance.agent.id],
                request=self.context.get('request')
            )
        if instance.profile.user_type == 'patient' and instance.profile.has_related_user_type:
            return reverse(
                viewname="patients:patient-detail",
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


class AccountSearchSerializer(serializers.Serializer):
    search = serializers.CharField(required=False, help_text='Patient number or national Id')

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class AccountVerifySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=8)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
