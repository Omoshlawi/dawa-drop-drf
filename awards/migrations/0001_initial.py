# Generated by Django 4.1.7 on 2023-04-30 05:48

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
            ],
        ),
        migrations.CreateModel(
            name='Reward',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('point_value', models.PositiveIntegerField(help_text='Number of points needed to redeem the reward')),
                ('max_redemptions', models.PositiveIntegerField(blank=True, help_text='Maximum number of times this reward can be redeemed', null=True)),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rewards', to='awards.loyaltyprogram')),
            ],
        ),
    ]