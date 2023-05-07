from django.contrib import admin

from .models import DeliverAgent


# Register your models here.
@admin.register(DeliverAgent)
class DeliverAgentAdmin(admin.ModelAdmin):
    list_display = ('id', "user", 'agent_number', 'delivery_mode', 'work_clinic', 'created_at')
