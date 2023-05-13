from django.db import models


# Create your models here.


# Toa medical specialties, staffing, equipment, bed capacity
class FacilityType(models.Model):
    remote_id = models.PositiveIntegerField(unique=True)
    level = models.PositiveIntegerField()
    name = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-level']

    def __str__(self):
        return self.name


class HealthFacility(models.Model):
    identification_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    type = models.ForeignKey(FacilityType, on_delete=models.CASCADE, related_name='facilities')
    longitude = models.DecimalField(max_digits=22, decimal_places=16)
    latitude = models.DecimalField(max_digits=22, decimal_places=16)
    address = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class FacilityTransferRequest(models.Model):
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name='transfer_requests'
    )
    hospital = models.ForeignKey(
        HealthFacility,
        related_name='transfer_requests',
        on_delete=models.CASCADE,
        help_text="Hospital requesting to transfer to"
    )
    reason = models.TextField(help_text="Reason for requesting facility Transfer")
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        'doctors.Doctor',
        related_name='transfer_approvals',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class DeliveryMode(models.Model):
    mode = models.CharField(unique=True, max_length=50)

    def __str__(self):
        return self.mode

    class Meta:
        ordering = ['-mode']


class MaritalStatus(models.Model):
    #   TODO remove the null when you clear the db
    remote_id = models.PositiveIntegerField(unique=True)
    status = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.status

    class Meta:
        ordering = ['-created_at']


class AppointMentType(models.Model):
    code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    remote_id = models.PositiveIntegerField(unique=True)
    type = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.type

    class Meta:
        ordering = ['-created_at']
