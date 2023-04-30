# Generated by Django 4.1.7 on 2023-04-30 12:46

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_patient_loyalty_program_redemption'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patient',
            name='next_of_keen',
        ),
        migrations.CreateModel(
            name='PatientNextOfKeen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='next_of_keen', to='users.patient')),
            ],
        ),
    ]
