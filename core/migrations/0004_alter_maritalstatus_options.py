# Generated by Django 4.1.7 on 2023-05-11 16:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_healthfacility_identification_code'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='maritalstatus',
            options={'ordering': ['-created_at']},
        ),
    ]