from django.db import models


# Create your models here.


# Toa medical specialties, staffing, equipment, bed capacity
class FacilityType(models.Model):
    level = models.PositiveIntegerField()
    name = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-level']

    def __str__(self):
        return self.name


class HealthFacility(models.Model):
    identification_code = models.CharField(max_length=50, unique=True, null=True, blank=True)
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
    status = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
# class DeliveryItem(models.Model):
#     """Models item to be delivered to the patient"""
#     name = models.CharField(max_length=)
