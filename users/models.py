# Create your models here.

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
