from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from django.urls import reverse

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

        if sociallogin.account.provider == 'google':
            email = sociallogin.account.extra_data.get('email')
            name = sociallogin.account.extra_data.get('name')
            profile = sociallogin.user.profile
            profile.google_email = email
            profile.google_name = name
            profile.save()

        elif sociallogin.account.provider == 'github':
            email = sociallogin.account.extra_data.get('email')
            login = sociallogin.account.extra_data.get('login')
            profile = sociallogin.user.profile
            profile.github_email = email
            profile.github_name = login
            profile.save()

        elif sociallogin.account.provider == 'facebook':  
            email = sociallogin.account.extra_data.get('email')
            name = sociallogin.account.extra_data.get('name')
            picture = sociallogin.account.extra_data.get('picture', {}).get('data', {}).get('url')

            profile = sociallogin.user.profile
            profile.facebook_email = email
            profile.facebook_name = name
            profile.facebook_profile_picture = picture
            profile.save()

    def get_login_redirect_url(self, request):
        return reverse('home')  

class MyFacebookOAuth2Adapter(FacebookOAuth2Adapter):
    """
    Custom Facebook OAuth2 Adapter to fetch email and profile picture correctly
    """
    def get_profile_url(self):
        return "https://graph.facebook.com/v12.0/me?fields=id,name,email,picture"
