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

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('home')  
        else:
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
        Profile.objects.create(user=user)  # Create an empty profile for the user

        messages.success(request, f"User {username} registered successfully. Please log in.")
        return redirect('login_view')

    return redirect('account_signup')

# Signal: Populate Profile after Social Signup
@receiver(user_signed_up)
def populate_profile_on_signup(request, sociallogin=None, **kwargs):
    user = kwargs['user']
    profile, created = Profile.objects.get_or_create(user=user)

    if sociallogin:
        extra_data = sociallogin.account.extra_data
        profile.profile_picture = extra_data.get('picture', '')

        if sociallogin.account.provider == 'google':
            profile.google_email = extra_data.get('email')
            profile.google_name = extra_data.get('name')

        elif sociallogin.account.provider == 'github':
            profile.github_email = extra_data.get('email')
            profile.github_name = extra_data.get('login')

        elif sociallogin.account.provider == 'facebook':
            profile.facebook_email = extra_data.get('email')
            profile.facebook_name = extra_data.get('name')
            profile.profile_picture = extra_data.get('picture', {}).get('data', {}).get('url')

    profile.save()

# Signal: Ensure Profile exists after Login
@receiver(user_logged_in)
def ensure_profile_on_login(request, **kwargs):
    user = kwargs['user']
    profile, created = Profile.objects.get_or_create(user=user)

    if user.socialaccount_set.exists():
        social_account = user.socialaccount_set.first()
        extra_data = social_account.extra_data

        if social_account.provider == 'google':
            profile.google_email = extra_data.get('email')
            profile.google_name = extra_data.get('name')

        elif social_account.provider == 'github':
            profile.github_email = extra_data.get('email')
            profile.github_name = extra_data.get('login')

        elif social_account.provider == 'facebook':
            profile.facebook_email = extra_data.get('email')
            profile.facebook_name = extra_data.get('name')
            profile.profile_picture = extra_data.get('picture', {}).get('data', {}).get('url')

        profile.save()

@login_required
def profile_page(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    # Extract country code and phone number
    if profile.phone and len(profile.phone) > 3:
        country_code = profile.phone[:3] if profile.phone.startswith("+") else ""
        phone_number = profile.phone[3:]  # Remaining digits
    else:
        country_code = ""
        phone_number = ""

    if request.method == "POST":
        first_name = request.POST.get('first_name', user.first_name)
        last_name = request.POST.get('last_name', user.last_name)
        gender = request.POST.get('gender', profile.gender)
        country = request.POST.get('country', profile.country)
        language = request.POST.get('language', profile.language)
        country_code = request.POST.get('country_code', country_code)
        phone_number = request.POST.get('phone_number', phone_number)

        # Save user details
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Save profile details
        profile.gender = gender
        profile.country = country
        profile.language = language
        profile.phone = f"{country_code}{phone_number}" if country_code and phone_number else None
        profile.save()

        return redirect('profile_page')

    return render(request, 'app/profile.html', {
        'profile': profile,
        'user': user,
        'default_country_code': country_code,
        'phone_number': phone_number,
    })
