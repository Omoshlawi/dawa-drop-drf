# Generated by Django 4.1.7 on 2023-04-27 15:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_alter_delivery_delivery_agent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delivery',
            name='order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='delivery', to='orders.order'),
        ),
    ]
