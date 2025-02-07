from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'google_name', 'github_name', 'linkedin_name')

    def email(self, obj):
        return obj.user.email  # Show email for manual users in admin panel

    email.admin_order_field = 'user__email'
    email.short_description = 'Email'
