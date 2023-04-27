# Generated by Django 4.1.7 on 2023-04-27 07:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='deliverymode',
            options={'ordering': ['-mode']},
        ),
        migrations.AlterModelOptions(
            name='hivclinic',
            options={'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='hivclinic',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
