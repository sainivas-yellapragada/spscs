from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'google_name', 'github_name', 'facebook_name', 'facebook_email', 'facebook_profile_pic')

    def email(self, obj):
        return obj.user.email  # Show email for manual users in admin panel

    email.admin_order_field = 'user__email'
    email.short_description = 'Email'

    # Custom method to display Facebook profile picture
    def facebook_profile_pic(self, obj):
        return f"<img src='{obj.facebook_profile_pic}' width='50' height='50'/>" if obj.facebook_profile_pic else "No Profile Pic"
    facebook_profile_pic.allow_tags = True
    facebook_profile_pic.short_description = 'Facebook Profile Picture'
