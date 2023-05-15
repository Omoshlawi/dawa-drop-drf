from django.contrib import admin

from medication.models import AppointMent, HIVLabTest, ARTRegimen, PatientHivMedication


# Register your models here.

class PatientLatTestInline(admin.TabularInline):
    model = HIVLabTest


@admin.register(AppointMent)
class AppointMentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'type', 'doctor', 'next_appointment_date', 'created_at', 'updated_at')
    inlines = [
        PatientLatTestInline
    ]


class AppointMentInline(admin.TabularInline):
    model = AppointMent


@admin.register(HIVLabTest)
class HIVLabTestAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'cd4_count', 'viral_load')


@admin.register(ARTRegimen)
class ARTRegimenAdmin(admin.ModelAdmin):
    list_display = ('id', 'regimen_line', 'regimen', 'created_at', 'updated_at')


@admin.register(PatientHivMedication)
class PatientHivMedicationAdmin(admin.ModelAdmin):
    list_display = ("patient", 'regimen', 'is_current', 'doctor', 'created_at', 'updated_at')


class PatientHivMedicationInline(admin.TabularInline):
    model = PatientHivMedication
