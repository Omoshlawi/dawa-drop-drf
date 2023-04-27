from django.contrib import admin

from core.models import HIVClinic, DeliveryMode


# Register your models here.


@admin.register(HIVClinic)
class HIVClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'longitude', 'latitude', 'address')


@admin.register(DeliveryMode)
class DeliveryModeAdmin(admin.ModelAdmin):
    list_display = ('mode',)
