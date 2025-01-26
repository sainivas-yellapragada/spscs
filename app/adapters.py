from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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
