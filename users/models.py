from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField

from awards.models import Reward, LoyaltyProgram, PatientProgramEnrollment
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


class Doctor(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='doctor')
    doctor_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    hiv_clinic = models.ForeignKey(HIVClinic, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Doctor {self.user.get_full_name()}"

    class Meta:
        ordering = ['-created_at']


class Patient(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='patient')
    patient_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    # TODO handle the cascade wisely
    base_clinic = models.ForeignKey(HIVClinic, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def current_program_enrollment(self):
        """Check if patient:
            1. Has enrolment marked current, if multiple return 1st assumed to be latest
            2. Is enrolled to any program but not marked current and if so marks latest current
            3. Is not enrolled but there is a default program and if so enrolls user to it
        :return None|PatientProgramEnrollment depending on conidtion
        """
        # 1
        enrollments = self.enrollments.filter(is_current=True)
        if enrollments.exists():
            enrollment = enrollments.first()
            return enrollment
        # 2.
        enrollments = self.enrollments.all()
        if enrollments.exists():
            enrollment = enrollments.first()
            enrollment.is_current = True
            enrollment.save()
            return enrollment
        # 3.
        programs = LoyaltyProgram.objects.filter(is_default=True)
        if programs.exists():
            enrollment = PatientProgramEnrollment.objects.create(
                patient=self,
                program=programs.first(),
                is_current=True
            )
            return enrollment
        return None

    @property
    def total_points(self):
        total_points = self.orders.all().aggregate(
            Sum('delivery__feedback__points_awarded')
        )['delivery__feedback__points_awarded__sum']
        points = total_points if total_points else 0
        return points

    @property
    def total_redemption_points(self):
        redeemed_points = self.redemptions.all().aggregate(
            Sum("points_redeemed")
        )['points_redeemed__sum']
        points = redeemed_points if redeemed_points else 0
        return points

    @property
    def points_balance(self):
        return self.total_points - self.total_redemption_points

    def __str__(self) -> str:
        return f"Patient {self.user.get_full_name()}"


class DeliverAgent(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='agent')
    agent_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    delivery_mode = models.ForeignKey(DeliveryMode, on_delete=models.CASCADE, related_name='agents')
    work_clinic = models.ForeignKey(HIVClinic, on_delete=models.CASCADE, related_name='agents')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

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

    class Meta:
        ordering = ['-created_at']


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
