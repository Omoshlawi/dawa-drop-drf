from django.db import models

# Create your models here.


class Doctor(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='doctor')
    doctor_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    hiv_clinic = models.ForeignKey("core.HealthFacility", on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Doctor {self.user.get_full_name()}"

    class Meta:
        ordering = ['-created_at']

