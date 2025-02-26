from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Profile
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, socialaccount):
        return True  

    def pre_social_login(self, request, sociallogin):
        google_id = sociallogin.account.extra_data.get('sub', '')

        if google_id:
            try:
                existing_user = User.objects.get(username=google_id)
                sociallogin.connect(request, existing_user)
                return
            except User.DoesNotExist:
                pass

        user = sociallogin.user
        if not user.pk:
            if not user.username:
                user.username = google_id or sociallogin.account.extra_data.get('email', '').split('@')[0]

        user.save()

        profile, created = Profile.objects.get_or_create(user=user)
        
        # Get login_type from GET first, then session
        login_type = request.GET.get('login_type', request.session.get('login_type', 'employee'))
        request.session['login_type'] = login_type
        request.session.save()  # Force session save
        logger.debug(f"Pre-social login: {user.username}, login_type={login_type}, session={request.session['login_type']}")

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
        login_type = request.session.get('login_type', 'employee')
        logger.debug(f"Social redirect for {request.user.username}, login_type={login_type}")
        return reverse('social_login_redirect')

class MyFacebookOAuth2Adapter(FacebookOAuth2Adapter):
    def get_profile_url(self):
        return "https://graph.facebook.com/v12.0/me?fields=id,name,email,picture"