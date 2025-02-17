from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to handle additional profile data and redirect after social login
    """
    
    def is_open_for_signup(self, request, socialaccount):
        return True  

    def pre_social_login(self, request, sociallogin):
        """
        Ensure users with the same Google ID are not duplicated and are linked instead.
        """
        google_id = sociallogin.account.extra_data.get('sub')  # 'sub' is Google user ID

        if google_id:
            try:
                existing_user = User.objects.get(username=google_id)
                sociallogin.connect(request, existing_user)  # Link existing user
                return  # Stop further processing
            except User.DoesNotExist:
                pass  # Continue with the signup process for new users

        user = sociallogin.user
        if not user.pk:
            if not user.username:
                user.username = google_id  # Set Google user ID as username

        user.save()

        # Now handle the profile
        profile, created = Profile.objects.get_or_create(user=user)

        extra_data = sociallogin.account.extra_data
        provider = sociallogin.account.provider

        if provider == 'google':
            profile.google_email = extra_data.get('email')
            profile.google_name = extra_data.get('name')
            profile.profile_picture = extra_data.get('picture', '')

        elif provider == 'github':
            profile.github_email = extra_data.get('email')
            profile.github_name = extra_data.get('login')

        elif provider == 'facebook':  
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
