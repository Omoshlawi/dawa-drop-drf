from django.contrib import admin

from orders.models import Order, Delivery, DeliveryFeedBack, AgentTrip


# Register your models here.


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'patient', 'national_id', 'date_of_depletion', 'reach_out_phone_number',
        'longitude', 'latitude', 'address', 'created_at', 'updated_at'
    )


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = (
        'order', 'code', 'created_at', 'delivery_medicine', 'doctor', 'delivery_agent', 'instruction'
    )
    list_editable = ('delivery_medicine', 'instruction', 'delivery_agent')
    list_filter = ('order__patient',)


@admin.register(DeliveryFeedBack)
class DeliveryFeedBackAdmin(admin.ModelAdmin):
    list_display = (
        'delivery', 'review', 'rating', 'created_at'
    )
    list_filter = ('delivery__order__patient',)


@admin.register(AgentTrip)
class AgentTripAdmin(admin.ModelAdmin):
    list_display = ('delivery', 'created_at', 'updated_at', 'longitude', 'latitude')
