# Generated by Django 4.1.7 on 2023-05-11 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='healthfacility',
            name='identification_code',
            field=models.CharField(default='5432', max_length=50, unique=True),
            preserve_default=False,
        ),
    ]