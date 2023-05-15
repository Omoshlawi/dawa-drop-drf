from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField


class Order(models.Model):
    reach_out_phone_number = PhoneNumberField(null=True, blank=True)
    appointment = models.OneToOneField(
        "medication.Appointment",
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    # todo think of the cascade
    delivery_mode = models.ForeignKey(
        "core.DeliveryMode",
        on_delete=models.CASCADE,
        related_name='orders',
        null=True, blank=True
    )
    time_slot = models.ForeignKey(
        'core.DeliveryTimeSlot',
        on_delete=models.CASCADE,
        related_name='orders',
        null=True, blank=True
    )
    longitude = models.DecimalField(max_digits=22, decimal_places=16)
    latitude = models.DecimalField(max_digits=22, decimal_places=16)
    address = models.CharField(max_length=300, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order {self.id}'

    def get_id(self):
        return f"KHMIS-DDOR-{self.created_at.year}-{self.id}"

    @property
    def is_delivered(self):
        return DeliveryFeedBack.objects.filter(delivery__order=self).exists()

    @property
    def is_allocated(self):
        return Delivery.objects.filter(order=self).exists()

    class Meta:
        ordering = ['-created_at']


class Delivery(models.Model):
    """Sore information of how orders were disbusted"""
    order = models.OneToOneField(Order, related_name='delivery', on_delete=models.CASCADE)
    code = models.CharField(max_length=32, unique=True, null=True, blank=True)
    prescription = models.ForeignKey(
        "medication.ARTRegimen",
        related_name='deliveries',
        on_delete=models.CASCADE
    )
    # todo Think about delete cascade
    delivery_agent = models.ForeignKey(
        "agents.DeliverAgent",
        related_name='deliveries',
        on_delete=models.CASCADE,
    )
    longitude = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True)
    latitude = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        null=True, blank=True,
        choices=(
            ('in_progress', 'in_progress'),
            ('canceled', 'canceled'),
        )
    )
    time_started = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_id(self):
        return f"KHMIS-DDDY-{self.created_at.year}-{self.id}"

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Delivery {self.id}"


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
    points_awarded = models.PositiveIntegerField(default=0)
    # awarded during creation
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"FeedBack {self.id}"

    class Meta:
        ordering = ['-created_at']


@receiver(post_save, sender=DeliveryFeedBack)
def create_check_user_program(sender, instance, created, **kwargs):
    """Check for patient point to see if he/she is eligible for moving to next programe"""
    # if created:
    #     patient = instance.delivery.order.patient
    #     points = patient.total_points
#        TODO ADD ALGORITHM TO MOVE USER TO NEXT PROGRAMME OF THRESHOLD POINT IS MET
