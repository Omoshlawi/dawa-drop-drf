from django.contrib import admin

from users.models import Profile


# Register your models here.

@admin.register(Profile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'image', 'phone_number')
    list_editable = ('gender', 'image', 'phone_number')
    list_filter = ('user', 'gender')
    search_fields = ('user', 'phone_number')
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'