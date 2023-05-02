from django.contrib import admin

from awards.models import LoyaltyProgram, Reward


# Register your models here.


@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit_point', 'point_rate', 'image', 'is_default', 'created_at')


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('name', 'program', 'point_value', 'image', 'max_redemptions', 'created_at')
