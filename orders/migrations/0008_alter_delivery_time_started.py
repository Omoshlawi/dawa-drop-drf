# Generated by Django 4.1.7 on 2023-05-15 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_delivery_time_started'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delivery',
            name='time_started',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
