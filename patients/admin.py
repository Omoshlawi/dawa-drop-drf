from django.contrib import admin

from awards.admin import PatientRedemptionInline, PatientProgramEnrollmentInline
from awards.models import PatientProgramEnrollment
from core.admin import TransferRequestInline
from .models import PatientNextOfKeen, Patient, AppointMent


# Register your models here.


@admin.register(PatientProgramEnrollment)
class PatientProgramEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'program', 'is_current', 'created_at', 'updated_at')


class PatientNextOfKeenInline(admin.TabularInline):
    model = PatientNextOfKeen


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("user", 'patient_number', 'base_clinic', 'created_at')
    inlines = [
        PatientProgramEnrollmentInline,
        PatientNextOfKeenInline,
        PatientRedemptionInline,
        TransferRequestInline,
    ]


class AppointMentInline(admin.TabularInline):
    model = AppointMent


@admin.register(AppointMent)
class AppointMentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'type', 'doctor', 'next_appointment_date', 'created_at', 'updated_at')
