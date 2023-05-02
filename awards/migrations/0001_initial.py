# Generated by Django 4.1.7 on 2023-05-02 06:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LoyaltyProgram',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the loyalty program', max_length=255)),
                ('unit_point', models.PositiveIntegerField(help_text='Number of points awarded on each successful order')),
                ('description', models.TextField(blank=True, null=True)),
                ('point_rate', models.DecimalField(decimal_places=2, help_text='Point worth in KES', max_digits=12)),
                ('image', models.ImageField(blank=True, null=True, upload_to='uploads/awards/programs')),
                ('is_default', models.BooleanField(default=False, help_text='Indicator if it can be assign to new patients by default')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Reward',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the program reward', max_length=255)),
                ('description', models.TextField()),
                ('point_value', models.PositiveIntegerField(help_text='Number of points needed to redeem the reward')),
                ('image', models.ImageField(blank=True, null=True, upload_to='uploads/awards/rewards')),
                ('max_redemptions', models.PositiveIntegerField(blank=True, help_text='Maximum number of times this reward can be redeemed', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rewards', to='awards.loyaltyprogram')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
