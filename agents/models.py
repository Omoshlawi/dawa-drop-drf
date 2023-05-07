from django.db import models

from doctors.models import Doctor
from patients.models import Patient


# Create your models here.


class DeliverAgent(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='agent')
    agent_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    delivery_mode = models.ForeignKey("core.DeliveryMode", on_delete=models.CASCADE, related_name='agents')
    work_clinic = models.ForeignKey("core.HealthFacility", on_delete=models.CASCADE, related_name='agents')
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

