# Generated by Django 4.1.7 on 2023-05-15 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_order_appointment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='delivery',
            name='delivery_medicine',
        ),
        migrations.RemoveField(
            model_name='delivery',
            name='doctor',
        ),
        migrations.RemoveField(
            model_name='delivery',
            name='instruction',
        ),
        migrations.RemoveField(
            model_name='order',
            name='patient',
        ),
        migrations.AddField(
            model_name='delivery',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=16, max_digits=22, null=True),
        ),
        migrations.AddField(
            model_name='delivery',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=16, max_digits=22, null=True),
        ),
        migrations.AddField(
            model_name='delivery',
            name='status',
            field=models.CharField(blank=True, choices=[('in_progress', 'in_progress'), ('canceled', 'canceled')], max_length=20, null=True),
        ),
        migrations.DeleteModel(
            name='AgentTrip',
        ),
    ]