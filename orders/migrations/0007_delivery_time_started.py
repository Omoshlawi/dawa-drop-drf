# Generated by Django 4.1.7 on 2023-05-15 20:55

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_delivery_prescription'),
    ]

    operations = [
        migrations.AddField(
            model_name='delivery',
            name='time_started',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
