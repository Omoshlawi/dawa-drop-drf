from django.db import models


# Create your models here.

class AppointMent(models.Model):
    patient = models.ForeignKey("patients.Patient", related_name='appointments', on_delete=models.CASCADE)
    type = models.ForeignKey('core.AppointMentType', related_name='appointments', on_delete=models.CASCADE)
    doctor = models.ForeignKey('auth.User', related_name='appoints', on_delete=models.CASCADE, )
    next_appointment_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.patient_number} {self.type} appointment"

    class Meta:
        ordering = ['-created_at']


class HIVLabTest(models.Model):
    appointment = models.ForeignKey(AppointMent, related_name='tests', on_delete=models.CASCADE)
    cd4_count = models.PositiveIntegerField()
    viral_load = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.appointment.patient} lab HIV test"

    class Meta:
        ordering = ['-appointment__created_at']


class ARTRegimen(models.Model):
    regimen_line = models.CharField(max_length=50, unique=True)
    regimen = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.regimen

    class Meta:
        ordering = ['-created_at']


class PatientHivMedication(models.Model):
    """
    HIV prescription
    """
    patient = models.ForeignKey('patients.Patient', related_name='prescriptions', on_delete=models.CASCADE)
    regimen = models.ForeignKey(ARTRegimen, related_name='prescriptions', on_delete=models.CASCADE)
    is_current = models.BooleanField(default=False)
    doctor = models.ForeignKey("auth.User", related_name='prescriptions', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} {self.regimen}"

    class Meta:
        ordering = ['-created_at']
