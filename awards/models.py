from django.db import models


# Create your models here.

class LoyaltyProgram(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the loyalty program")
    unit_point = models.PositiveIntegerField(help_text="Number of points awarded on each successful order")
    description = models.TextField(null=True, blank=True)
    point_rate = models.DecimalField(decimal_places=2, max_digits=12, help_text='Point worth in KES')
    image = models.ImageField(upload_to='uploads/awards/programs', null=True, blank=True)
    is_default = models.BooleanField(default=False,
                                     help_text="Indicator if it can be assign to new patients by default")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def members(self):
        return self.enrollments.all()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class Reward(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the program reward")
    program = models.ForeignKey(LoyaltyProgram, related_name='rewards', on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    point_value = models.PositiveIntegerField(help_text='Number of points needed to redeem the reward')
    image = models.ImageField(upload_to='uploads/awards/rewards', null=True, blank=True)
    max_redemptions = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Maximum number of times this reward can be redeemed'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class PatientProgramEnrollment(models.Model):
    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE, related_name='enrollments')
    # todo think of ondelete
    program = models.ForeignKey(
        LoyaltyProgram,
        on_delete=models.CASCADE,
        related_name='enrollments',
        null=True,
        blank=True
    )
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['patient', 'program']

    def __str__(self):
        return f"{self.patient.user.get_full_name()} {self.program.name} Enrollment"


class Redemption(models.Model):
    patient = models.ForeignKey("patients.Patient", related_name='redemptions', on_delete=models.CASCADE)
    points_redeemed = models.PositiveIntegerField()
    reward = models.ForeignKey(Reward, related_name='redemptions', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
