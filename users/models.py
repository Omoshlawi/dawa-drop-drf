from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField

from awards.models import Reward, LoyaltyProgram
from core.models import HIVClinic, DeliveryMode

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

    @property
    def has_related_user_type(self) -> bool:
        if self.user_type == 'patient':
            return bool(Patient.objects.filter(user=self.user))
        if self.user_type == 'doctor':
            return bool(Doctor.objects.filter(user=self.user))
        if self.user_type == 'agent':
            return bool(DeliverAgent.objects.filter(user=self.user))


class Doctor(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='doctor')
    doctor_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    hiv_clinic = models.ForeignKey(HIVClinic, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Doctor {self.user.get_full_name()}"


class Patient(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='patient')
    patient_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    base_clinic = models.ForeignKey(HIVClinic, on_delete=models.CASCADE, null=True, blank=True)
    # TODO handle the cascade wisely
    loyalty_program = models.ForeignKey(
        LoyaltyProgram,
        on_delete=models.CASCADE,
        related_name='patients',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Patient {self.user.get_full_name()}"


class Redemption(models.Model):
    patient = models.ForeignKey(Patient, related_name='redemptions', on_delete=models.CASCADE)
    points_redeemed = models.PositiveIntegerField()
    reward = models.ForeignKey(Reward, related_name='redemptions', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class DeliverAgent(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='agent')
    agent_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    delivery_mode = models.ForeignKey(DeliveryMode, on_delete=models.CASCADE, related_name='agents')
    work_clinic = models.ForeignKey(HIVClinic, on_delete=models.CASCADE, related_name='agents')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Agent {self.user.get_full_name()}"

    def to_patient(self):
        patient = Patient.objects.create(
            user=self.user,
            base_clinic=self.work_clinic,
        )
        DeliverAgent.objects.delete(id=self.id)
        return patient

    def to_doctor(self):
        doctor = Doctor.objects.create(
            user=self.user,
            hiv_clinic=self.work_clinic
        )
        DeliverAgent.objects.delete(id=self.id)
        return doctor


class PatientNextOfKeen(models.Model):
    patient = models.ForeignKey(Patient, related_name='next_of_keen', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    # create profile
    if created:
        Profile.objects.create(user=instance)


# @receiver(pre_save, sender=User)
# def check_email(sender, instance, **kwargs):
#     email = instance.email
#     if sender.objects.filter(email=email).exclude(username=instance.username).exists():
#         raise ValidationError('Email Already Exists')
