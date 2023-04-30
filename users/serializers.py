from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework.reverse import reverse
from rest_framework_nested import serializers as nested_serializer
from core.models import HIVClinic
from users.models import Profile, Doctor, Patient, DeliverAgent, USER_TYPE_CHOICES, GENDER_CHOICES, PatientNextOfKeen


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


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('gender', 'image', 'phone_number', 'address', 'user_type')
        extra_kwargs = {
            'user_type': {'read_only': True}
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

    class Meta:
        model = User
        fields = ['url', 'email']

    def to_representation(self, instance):
        _dict = super().to_representation(instance)
        profile = PublicProfileSerializer(instance=instance.profile, context=self.context).data
        _dict.update(profile)
        return _dict


class DoctorSerializer(serializers.ModelSerializer):
    hiv_clinic = serializers.HyperlinkedRelatedField(
        view_name='core:clinic-detail', queryset=HIVClinic.objects.all()
    )

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
    url = nested_serializer.NestedHyperlinkedIdentityField(
        view_name='users:next-of-keen-detail',
        parent_lookup_kwargs={'patient_pk': 'patient__pk'},
        many=True, read_only=True
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
    next_of_keen = nested_serializer.NestedHyperlinkedIdentityField(
        view_name='users:next-of-keen-detail',
        parent_lookup_kwargs={'patient_pk': 'patient__pk'},
        many=True, read_only=True
    )

    def to_representation(self, instance):
        _dict = super().to_representation(instance)
        next_of_keen_urls = _dict.pop("next_of_keen")
        next_of_keen_obj = {
            'next_of_keen': {
                'count': len(next_of_keen_urls),
                'next_of_keens': reverse(
                    viewname='users:next-of-keen-list',
                    args=[instance.id],
                    request=self.context.get('request')
                ),
                'urls': next_of_keen_urls
            }
        }
        _dict.update(next_of_keen_obj)
        return _dict

    class Meta:
        model = Patient
        fields = (
            'url',
            'patient_number', 'next_of_keen',
            'base_clinic',
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


class UserProfileSerializer(serializers.ModelSerializer):
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
