from django.shortcuts import render, redirect
from django.contrib.auth import logout
from allauth.account.signals import user_signed_up, user_logged_in
from django.dispatch import receiver
from .models import Profile
from django.contrib.auth.decorators import login_required

# Index view - Displays the custom login page
def login(request):
    return render(request, 'app/login.html')  # Custom login page

# Home view - Displays the homepage with user and profile details
@login_required  # Ensure only authenticated users can access the homepage
def home(request):
    profile = Profile.objects.filter(user=request.user).first()  # Get the user's profile
    return render(request, 'app/home.html', {  # Updated to use 'app/home.html' for homepage
        'user': request.user,
        'profile': profile,
    })

# Logout view - Logs out the user and redirects to the login page
def logout_view(request):
    logout(request)
    return redirect('index')  # Redirect to login page after logout

# Signal to populate the Profile with social login details after signup
@receiver(user_signed_up)
def populate_profile_on_signup(sociallogin, **kwargs):
    user = sociallogin.user
    profile, created = Profile.objects.get_or_create(user=user)

    # Log the data received from social accounts
    print(f"{sociallogin.account.provider.capitalize()} Data:", sociallogin.account.extra_data)

    if sociallogin.account.provider == 'google':
        profile.google_email = sociallogin.account.extra_data.get('email')
        profile.google_name = sociallogin.account.extra_data.get('name')
    elif sociallogin.account.provider == 'github':
        profile.github_email = sociallogin.account.extra_data.get('email')
        profile.github_name = sociallogin.account.extra_data.get('login')
    elif sociallogin.account.provider == 'linkedin':
        profile.linkedin_email = sociallogin.account.extra_data.get('emailAddress')
        profile.linkedin_name = f"{sociallogin.account.extra_data.get('localizedFirstName')} {sociallogin.account.extra_data.get('localizedLastName')}"
        profile.linkedin_profile_pic = sociallogin.account.extra_data.get('profilePicture(displayImage~:playableStreams)')
    
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
        elif social_account.provider == 'linkedin':  # LinkedIn
            profile.linkedin_email = social_account.extra_data.get('emailAddress')
            profile.linkedin_name = f"{social_account.extra_data.get('localizedFirstName')} {social_account.extra_data.get('localizedLastName')}"
            profile.linkedin_profile_pic = social_account.extra_data.get('profilePicture(displayImage~:playableStreams)')
        profile.save()
