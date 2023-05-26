from django.contrib import admin

from .models import LoyaltyProgram, Reward, PatientProgramEnrollment, Redemption


# Register your models here.


class RewardInline(admin.TabularInline):
    model = Reward


class PatientProgramEnrollmentInline(admin.TabularInline):
    model = PatientProgramEnrollment


@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'unit_point', 'point_rate', 'image',
        'is_default', 'entry_points', 'created_at'
    )
    list_editable = (
        'unit_point', 'point_rate', 'image',
        'is_default', 'entry_points'
    )
    inlines = [RewardInline]


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('name', 'program', 'point_value', 'image', 'max_redemptions', 'created_at')


class PatientRedemptionInline(admin.TabularInline):
    model = Redemption


@admin.register(Redemption)
class RedemptionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'points_redeemed', 'reward', 'created_at')
