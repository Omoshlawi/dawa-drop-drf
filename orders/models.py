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
    date_of_depletion = models.DateField(default=timezone.now)
    reach_out_phone_number = PhoneNumberField(null=True, blank=True)
    longitude = models.DecimalField(max_digits=22, decimal_places=16)
    latitude = models.DecimalField(max_digits=22, decimal_places=16)
    address = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order {self.id}'

    class Meta:
        ordering = ['-created_at']


class Delivery(models.Model):
    order = models.OneToOneField(Order, related_name='order', on_delete=models.CASCADE)
    code = models.CharField(max_length=32, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_medicine = models.CharField(max_length=255, blank=True, null=True)
    instruction = models.TextField(null=True, blank=True)
    doctor = models.ForeignKey(Doctor, related_name='deliveries', on_delete=models.CASCADE)
    # todo Think about delete cascade
    delivery_agent = models.ForeignKey(DeliverAgent, related_name='deliveries', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']


class DeliveryFeedBack(models.Model):
    delivery = models.OneToOneField(Delivery, related_name='feedback', on_delete=models.CASCADE)
    review = models.TextField()
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


@receiver(post_save, sender=Order)
def create_order_deliver(sender, instance, created, **kwargs):
    """
       Generate unique delivery code for every order made
    """
    if created:
        # Generate a 32-character string
        random_string = secrets.token_hex(16)
        # make sure its unique
        while Delivery.objects.filter(code=random_string):
            random_string = secrets.token_hex(16)
        # create delivery object
        Delivery.objects.create(
            order=instance,
            code=random_string
        )
