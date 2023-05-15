from django.contrib import admin

from orders.models import Order, Delivery, DeliveryFeedBack


# Register your models here.


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'appointment', 'reach_out_phone_number', 'delivery_mode', 'time_slot',
        'longitude', 'latitude', 'address', 'created_at', 'updated_at'
    )


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = (
        'order', 'code', 'created_at', 'delivery_agent', 'longitude', 'latitude', 'status'
    )
    list_filter = ('order__appointment__patient',)


@admin.register(DeliveryFeedBack)
class DeliveryFeedBackAdmin(admin.ModelAdmin):
    list_display = (
        'delivery', 'review', 'rating', 'created_at'
    )
    list_filter = ('delivery__order__appointment__patient',)

