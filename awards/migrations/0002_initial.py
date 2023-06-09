# Generated by Django 4.1.7 on 2023-05-16 08:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('awards', '0001_initial'),
        ('patients', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='redemption',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='redemptions', to='patients.patient'),
        ),
        migrations.AddField(
            model_name='redemption',
            name='reward',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='redemptions', to='awards.reward'),
        ),
        migrations.AddField(
            model_name='patientprogramenrollment',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='patients.patient'),
        ),
        migrations.AddField(
            model_name='patientprogramenrollment',
            name='program',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='awards.loyaltyprogram'),
        ),
        migrations.AlterUniqueTogether(
            name='patientprogramenrollment',
            unique_together={('patient', 'program')},
        ),
    ]
