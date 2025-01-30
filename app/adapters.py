from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to handle additional profile data and redirect after social login
    """
    
    def is_open_for_signup(self, request, socialaccount):
        """
        Custom logic to handle if the social account can be linked with the current user
        """
        return True  # Modify as needed for your logic
    
    def pre_social_login(self, request, sociallogin):
        """
        Handle user data before the social login process
        """
        super().pre_social_login(request, sociallogin)
        
        # Handle custom user profile information from social login
        if sociallogin.account.provider == 'google':
            # Example: Populate user profile from Google data
            email = sociallogin.account.extra_data.get('email')
            name = sociallogin.account.extra_data.get('name')
            profile = sociallogin.user.profile
            profile.google_email = email
            profile.google_name = name
            profile.save()

        elif sociallogin.account.provider == 'github':
            # Example: Populate user profile from GitHub data
            email = sociallogin.account.extra_data.get('email')
            login = sociallogin.account.extra_data.get('login')
            profile = sociallogin.user.profile
            profile.github_email = email
            profile.github_name = login
            profile.save()

        elif sociallogin.account.provider == 'linkedin':
            # Example: Populate user profile from LinkedIn data
            email = sociallogin.account.extra_data.get('emailAddress')
            first_name = sociallogin.account.extra_data.get('localizedFirstName')
            last_name = sociallogin.account.extra_data.get('localizedLastName')
            profile = sociallogin.user.profile
            profile.linkedin_email = email
            profile.linkedin_name = f"{first_name} {last_name}"
            profile.save()
    
    def get_login_redirect_url(self, request):
        """
        Define the URL to redirect after successful social login
        """
        # After login, redirect to the homepage or another desired URL
        return reverse('home')
