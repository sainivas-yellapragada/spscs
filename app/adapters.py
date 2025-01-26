from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # If the user is already logged in, don't link anything
        if request.user.is_authenticated:
            return

        # Fetch the email from the social account
        email = sociallogin.account.extra_data.get('email')

        # Check if a user with this email exists
        if email:
            try:
                existing_user = User.objects.get(email=email)
                sociallogin.connect(request, existing_user)  # Link the social account
            except User.DoesNotExist:
                pass  # No user exists, proceed with normal signup

    def save_user(self, request, sociallogin, form=None):
        # Save the user instance
        user = super().save_user(request, sociallogin, form)
        
        # Create or get the profile for the user
        profile, created = Profile.objects.get_or_create(user=user)
        
        # Handle social login data based on provider
        if sociallogin.account.provider == 'google':
            profile.google_email = sociallogin.account.extra_data.get('email')
            profile.google_name = sociallogin.account.extra_data.get('name')
        elif sociallogin.account.provider == 'github':
            profile.github_email = sociallogin.account.extra_data.get('email')
            profile.github_name = sociallogin.account.extra_data.get('login')
        elif sociallogin.account.provider == 'linkedin':
            # LinkedIn specific data handling
            profile.linkedin_email = sociallogin.account.extra_data.get('emailAddress')
            profile.linkedin_name = f"{sociallogin.account.extra_data.get('localizedFirstName')} {sociallogin.account.extra_data.get('localizedLastName')}"
            profile.linkedin_profile_pic = sociallogin.account.extra_data.get('profilePicture(displayImage~:playableStreams)')

        # Save the profile data
        profile.save()
        
        return user
