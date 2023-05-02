from django.contrib import admin

from core.models import HIVClinic, DeliveryMode, TransferRequest


# Register your models here.


@admin.register(HIVClinic)
class HIVClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'longitude', 'latitude', 'address')


@admin.register(DeliveryMode)
class DeliveryModeAdmin(admin.ModelAdmin):
    list_display = ('mode',)


@admin.register(TransferRequest)
class TransferRequestAdmin(admin.ModelAdmin):
    list_display = (
        'patient', 'hospital', 'reason',
        'is_approved', 'approved_by', 'created_at',
        'updated_at'
    )


class TransferRequestInline(admin.TabularInline):
    model = TransferRequest
