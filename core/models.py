from django.db import models


# Create your models here.


class HIVClinic(models.Model):
    name = models.CharField(max_length=100)
    longitude = models.DecimalField(max_digits=22, decimal_places=16)
    latitude = models.DecimalField(max_digits=22, decimal_places=16)
    address = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class DeliveryMode(models.Model):
    mode = models.CharField(unique=True, max_length=50)

    def __str__(self):
        return self.mode

    class Meta:
        ordering = ['-mode']

# class DeliveryItem(models.Model):
#     """Models item to be delivered to the patient"""
#     name = models.CharField(max_length=)
