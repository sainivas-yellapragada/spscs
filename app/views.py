from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from allauth.account.signals import user_signed_up, user_logged_in
from django.dispatch import receiver
from .models import Profile

# Custom login page
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Debugging: Print out the entered username and password
        print(f"Attempting login with username: {username}, password: {password}")

        # Check if user exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            print(f"User '{username}' does not exist")
            messages.error(request, "Invalid credentials. Please try again.")
            return redirect('login_view')

        # Attempt to authenticate the user
        user = authenticate(request, username=username, password=password)

        # Check if authentication is successful
        if user is not None:
            print(f"User '{username}' authenticated successfully!")
            auth_login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('home')  # Redirect to home page after successful login
        else:
            print(f"Authentication failed for username: {username}")
            messages.error(request, "Invalid credentials. Please try again.")
            return redirect('login_view')

    return render(request, 'app/login.html')

# Home page (protected)
@login_required
def home(request):
    profile = Profile.objects.filter(user=request.user).first()
    return render(request, 'app/home.html', {'user': request.user, 'profile': profile})

# Logout user
def logout_view(request):
    logout(request)
    return redirect('index')

# User registration (Manual)
def manual_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.warning(request, "Username already exists! Please log in.")
            return redirect('login_view')

        if User.objects.filter(email=email).exists():
            messages.warning(request, "Email already registered! Please log in.")
            return redirect('login_view')

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password1)

        messages.success(request, f"User {username} registered successfully. Please log in.")
        return redirect('login_view')

    return redirect('account_signup')

# Signal: Populate Profile after Social Signup
@receiver(user_signed_up)
def populate_profile_on_signup(request, sociallogin=None, **kwargs):
    user = kwargs['user']
    profile, created = Profile.objects.get_or_create(user=user)

    # If it's a social login, populate profile data
    if sociallogin:
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

# Signal: Ensure Profile exists after Login
@receiver(user_logged_in)
def ensure_profile_on_login(request, **kwargs):
    user = kwargs['user']
    profile, created = Profile.objects.get_or_create(user=user)

    if user.socialaccount_set.exists():
        social_account = user.socialaccount_set.first()
        if social_account.provider == 'google':
            profile.google_email = social_account.extra_data.get('email')
            profile.google_name = social_account.extra_data.get('name')
        elif social_account.provider == 'github':
            profile.github_email = social_account.extra_data.get('email')
            profile.github_name = social_account.extra_data.get('login')
        elif social_account.provider == 'linkedin':
            profile.linkedin_email = social_account.extra_data.get('emailAddress')
            profile.linkedin_name = f"{social_account.extra_data.get('localizedFirstName')} {social_account.extra_data.get('localizedLastName')}"
            profile.linkedin_profile_pic = social_account.extra_data.get('profilePicture(displayImage~:playableStreams)')
        profile.save()
