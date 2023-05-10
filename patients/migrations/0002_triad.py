# Generated by Django 4.1.7 on 2023-05-10 07:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Triad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.DecimalField(decimal_places=2, max_digits=12)),
                ('height', models.DecimalField(decimal_places=2, max_digits=12)),
                ('blood_pressure', models.DecimalField(decimal_places=2, max_digits=12)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='triads', to='patients.patient')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
