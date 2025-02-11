from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from django.urls import reverse
from .models import Profile

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to handle additional profile data and redirect after social login
    """
    
    def is_open_for_signup(self, request, socialaccount):
        return True  

    def pre_social_login(self, request, sociallogin):
        """
        Handle user data before the social login process
        """
        super().pre_social_login(request, sociallogin)

        profile, created = Profile.objects.get_or_create(user=sociallogin.user)

        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data
            profile.google_email = extra_data.get('email')
            profile.google_name = extra_data.get('name')
            profile.profile_picture = extra_data.get('picture', '')

        elif sociallogin.account.provider == 'github':
            extra_data = sociallogin.account.extra_data
            profile.github_email = extra_data.get('email')
            profile.github_name = extra_data.get('login')

        elif sociallogin.account.provider == 'facebook':  
            extra_data = sociallogin.account.extra_data
            profile.facebook_email = extra_data.get('email')
            profile.facebook_name = extra_data.get('name')
            profile.profile_picture = extra_data.get('picture', {}).get('data', {}).get('url')

        profile.save()

    def get_login_redirect_url(self, request):
        return reverse('home')  

class MyFacebookOAuth2Adapter(FacebookOAuth2Adapter):
    """
    Custom Facebook OAuth2 Adapter to fetch email and profile picture correctly
    """
    def get_profile_url(self):
        return "https://graph.facebook.com/v12.0/me?fields=id,name,email,picture"
