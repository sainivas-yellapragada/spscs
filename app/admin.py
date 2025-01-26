from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'google_email', 'google_name',
                    'github_email', 'github_name', 
                    'linkedin_email', 'linkedin_name', 'linkedin_profile_pic')
