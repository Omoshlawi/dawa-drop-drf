from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField

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
    ('soctor', 'doctor'),
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
    created_at = models.DateField(auto_now=True)
    updated_at = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username}'s Profile"


class Doctor(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='doctor')
    doctor_number = models.CharField(max_length=50, unique=True, null=False, blank=False)
    hiv_clinic = models.ForeignKey(HIVClinic, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now=True)
    updated_at = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Doctor {self.user.get_full_name()}"


class Patient(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='patient')
    patient_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    next_of_keen = models.CharField(max_length=255, blank=True, null=False)
    base_clinic = models.ForeignKey(HIVClinic, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now=True)
    updated_at = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Patient {self.user.get_full_name()}"


class DeliverAgent(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='agent')
    agent_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    delivery_mode = models.ForeignKey(DeliveryMode, on_delete=models.CASCADE, related_name='agents')
    created_at = models.DateField(auto_now=True)
    updated_at = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Agent {self.user.get_full_name()}"


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    # create profile
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=Profile)
def create_user_type(sender, instance, created, **kwargs):
    # TODO Implement logi for user types
    if instance.user_type == 'agent':
        # Perform agent operation
        pass
    elif instance.user_type == 'doctor':
        # perform doctor operation
        pass
    else:
        # perform patient operation
        pass
