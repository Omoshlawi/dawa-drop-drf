from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models import Profile


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="users:user-detail")
    is_staff = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'first_name', 'last_name', 'is_staff']


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
        return super().update(instance, validated_data)

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
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
        fields = ('gender', 'image', 'phone_number')


class UserProfileSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(read_only=True)
    profile = ProfileSerializer()
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile")
        try:
            profile = instance.profile
            if profile:
                for key in profile_data:
                    # Check if image is unmordified then avoid resaving
                    if key == 'image' and str(profile_data[key]) == str(profile.image).split("/")[-1]:
                        continue
                    setattr(profile, key, profile_data[key])
                profile.save()
        except ObjectDoesNotExist:
            Profile.objects.create(user=instance, **profile_data)
        return super().update(instance, validated_data)
