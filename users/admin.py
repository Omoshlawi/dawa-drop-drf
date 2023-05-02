from django.contrib import admin

from users.models import Profile, Doctor, Patient, DeliverAgent, PatientNextOfKeen, Redemption


# Register your models here.

@admin.register(Profile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'image', 'phone_number')
    list_editable = ('gender', 'image', 'phone_number')
    list_filter = ('user', 'gender')
    search_fields = ('user', 'phone_number')
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("user", 'doctor_number', 'hiv_clinic', 'created_at')


class PatientRedemptionInline(admin.TabularInline):
    model = Redemption


class PatientNextOfKeenInline(admin.TabularInline):
    model = PatientNextOfKeen


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("user", 'patient_number', 'base_clinic', 'created_at')
    inlines = [PatientNextOfKeenInline, PatientRedemptionInline]


@admin.register(DeliverAgent)
class DeliverAgentAdmin(admin.ModelAdmin):
    list_display = ('id', "user", 'agent_number', 'delivery_mode', 'work_clinic', 'created_at')
