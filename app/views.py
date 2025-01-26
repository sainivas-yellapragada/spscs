from django.shortcuts import render, redirect
from django.contrib.auth import logout
from allauth.account.signals import user_signed_up, user_logged_in
from django.dispatch import receiver
from .models import Profile

# Home view - Displays the homepage with user and profile details
def home(request):
    profile = None
    if request.user.is_authenticated:
        # Retrieve the logged-in user's profile
        profile = Profile.objects.filter(user=request.user).first()
    return render(request, 'app/index.html', {
        'user': request.user,
        'profile': profile,
    })

# Logout view - Logs out the user and redirects to the homepage
def logout_view(request):
    logout(request)
    return redirect('/')

# Signal to populate the Profile with social login details after signup
@receiver(user_signed_up)
def populate_profile_on_signup(sociallogin, **kwargs):
    user = sociallogin.user
    profile, created = Profile.objects.get_or_create(user=user)

    # Log the data received from GitHub
    print("GitHub Data:", sociallogin.account.extra_data)

    if sociallogin.account.provider == 'google':
        profile.google_email = sociallogin.account.extra_data.get('email')
        profile.google_name = sociallogin.account.extra_data.get('name')
    elif sociallogin.account.provider == 'github':
        profile.github_email = sociallogin.account.extra_data.get('email')  # May return None if private
        profile.github_name = sociallogin.account.extra_data.get('login')  # GitHub username
    profile.save()

# Signal to ensure a Profile is created or updated after login
@receiver(user_logged_in)
def ensure_profile_on_login(request, **kwargs):
    user = kwargs['user']
    profile, created = Profile.objects.get_or_create(user=user)  # Ensure Profile exists

    # If it's a social login, update details
    if user.socialaccount_set.exists():
        social_account = user.socialaccount_set.first()  # Get the first social account
        if social_account.provider == 'google':  # Google
            profile.google_email = social_account.extra_data.get('email')
            profile.google_name = social_account.extra_data.get('name')
        elif social_account.provider == 'github':  # GitHub
            profile.github_email = social_account.extra_data.get('email')
            profile.github_name = social_account.extra_data.get('login')
        profile.save()
