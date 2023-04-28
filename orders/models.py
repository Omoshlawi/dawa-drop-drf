from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
import secrets
from django.utils import timezone

from users.models import Doctor, DeliverAgent


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    national_id = models.PositiveIntegerField()
    date_of_depletion = models.DateField()
    reach_out_phone_number = PhoneNumberField(null=True, blank=True)
    longitude = models.DecimalField(max_digits=22, decimal_places=16)
    latitude = models.DecimalField(max_digits=22, decimal_places=16)
    address = models.CharField(max_length=300, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order {self.id}'

    def get_id(self):
        return f"KHMIS-DDOR-{self.created_at.year}-{self.id}"

    class Meta:
        ordering = ['-created_at']


class Delivery(models.Model):
    order = models.OneToOneField(Order, related_name='delivery', on_delete=models.CASCADE)
    code = models.CharField(max_length=32, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_medicine = models.CharField(max_length=255, blank=True, null=True)
    instruction = models.TextField(null=True, blank=True)
    doctor = models.ForeignKey(
        Doctor,
        related_name='deliveries',
        on_delete=models.CASCADE
    )
    # todo Think about delete cascade
    delivery_agent = models.ForeignKey(
        DeliverAgent,
        related_name='deliveries',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.user.get_full_name()}'s Delivery"


class DeliveryFeedBack(models.Model):
    delivery = models.OneToOneField(Delivery, related_name='feedback', on_delete=models.CASCADE)
    review = models.TextField(blank=True, null=True)
    rating = models.IntegerField(
        choices=(
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4'),
            (5, '5')
        )
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
