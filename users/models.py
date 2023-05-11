# Create your models here.
import secrets

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField

from agents.models import DeliverAgent
from awards.models import LoyaltyProgram, PatientProgramEnrollment
from doctors.models import Doctor
from patients.models import Patient

# Create your models here.
GENDER_CHOICES = (
    ('male', 'male'),
    ('female', 'female'),
    ('other', 'other')
)

USER_TYPE_CHOICES = (
    ('agent', 'agent'),
    ('patient', 'patient'),
    ('doctor', 'doctor'),
)


class Profile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    image = models.ImageField(
        null=True,
        upload_to='uploads/profile',
        blank=True,
    )
    address = models.CharField(max_length=255, null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    user_type = models.CharField(choices=USER_TYPE_CHOICES, default='patient', max_length=20)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username}'s Profile"

    class Meta:
        ordering = ['-created_at']

    @property
    def has_related_user_type(self) -> bool:
        if self.user_type == 'patient':
            return Patient.objects.filter(user=self.user).exists()
        if self.user_type == 'doctor':
            return Doctor.objects.filter(user=self.user).exists()
        if self.user_type == 'agent':
            return DeliverAgent.objects.filter(user=self.user).exists()


class AccountVerification(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    code = models.CharField(max_length=4, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    search_value = models.CharField(max_length=50)
    extra_data = models.CharField(max_length=255)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    # create profile
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=AccountVerification)
def generate_unique_verification_code(sender, instance, created, **kwargs):
    if created:
        random_string = secrets.token_hex(2)
        # make sure there exist no other unverified verification with generated code
        while AccountVerification.objects.filter(code=random_string,is_verified=False).exists():
            random_string = secrets.token_hex(2)
        instance.code = random_string
        instance.save()

# @receiver(pre_save, sender=User)
# def check_email(sender, instance, **kwargs):
#     email = instance.email
#     if sender.objects.filter(email=email).exclude(username=instance.username).exists():
#         raise ValidationError('Email Already Exists')
