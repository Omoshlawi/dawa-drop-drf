# Generated by Django 4.1.7 on 2023-05-14 07:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_alter_order_time_slot'),
        ('agents', '0003_deliverytimeslot'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DeliveryTimeSlot',
        ),
    ]