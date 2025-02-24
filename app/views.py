from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from allauth.account.signals import user_signed_up, user_logged_in
from django.dispatch import receiver
from .models import Profile, Project,Whiteboard
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
import json

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
    projects = Project.objects.filter(team_members=request.user)
    team_members_dict = {}

    for project in projects:
        for member in project.team_members.all():
            if member != request.user:
                if member not in team_members_dict:
                    team_members_dict[member] = []
                team_members_dict[member].append(project.title)

    return render(request, 'app/home.html', {
        'user': request.user,
        'profile': profile,
        'team_members_dict': team_members_dict
    })

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

        user = User.objects.create_user(username=username, email=email, password=password1)
        Profile.objects.create(user=user)

        messages.success(request, f"User {username} registered successfully. Please log in.")
        return redirect('login_view')

    return redirect('account_signup')

# Signal: Populate Profile after Social Signup
@receiver(user_signed_up)
def populate_profile_on_signup(request, sociallogin=None, **kwargs):
    user = kwargs['user']
    profile, _ = Profile.objects.get_or_create(user=user)

    if sociallogin:
        extra_data = sociallogin.account.extra_data
        profile.profile_picture = extra_data.get('picture', '')

        provider_map = {
            'google': ('google_email', 'google_name'),
            'github': ('github_email', 'github_name'),
            'facebook': ('facebook_email', 'facebook_name')
        }

        if sociallogin.account.provider in provider_map:
            email_field, name_field = provider_map[sociallogin.account.provider]
            setattr(profile, email_field, extra_data.get('email'))
            setattr(profile, name_field, extra_data.get('name'))


        profile.save()

# Signal: Ensure Profile exists after Login
@receiver(user_logged_in)
def ensure_profile_on_login(request, **kwargs):
    user = kwargs['user']
    profile, _ = Profile.objects.get_or_create(user=user)

    if user.socialaccount_set.exists():
        social_account = user.socialaccount_set.first()
        extra_data = social_account.extra_data

        provider_map = {
            'google': ('google_email', 'google_name'),
            'github': ('github_email', 'github_name'),
            'facebook': ('facebook_email', 'facebook_name')
        }

        if social_account.provider in provider_map:
            email_field, name_field = provider_map[social_account.provider]
            setattr(profile, email_field, extra_data.get('email'))
            setattr(profile, name_field, extra_data.get('name'))

        profile.save()

@login_required
def profile_page(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    country_code, phone_number = "", ""
    if profile.phone:
        country_code, phone_number = (profile.phone[:3], profile.phone[3:]) if profile.phone.startswith("+") else ("", profile.phone)

    if request.method == "POST":
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.save()

        profile.gender = request.POST.get('gender', profile.gender)
        profile.country = request.POST.get('country', profile.country)
        profile.language = request.POST.get('language', profile.language)
        country_code = request.POST.get('country_code', country_code)
        phone_number = request.POST.get('phone_number', phone_number)

        profile.phone = f"{country_code}{phone_number}" if country_code and phone_number else None
        profile.save()

        return redirect('profile_page')

    return render(request, 'app/profile.html', {
        'profile': profile,
        'user': user,
        'default_country_code': country_code,
        'phone_number': phone_number,
    })

@login_required
def projects(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)  # Ensure profile exists
    user_projects = Project.objects.filter(team_members=request.user)
    users = User.objects.all()
    
    return render(request, 'app/projects.html', {
        'projects': user_projects, 
        'users': users,
        'profile': profile  # Add profile to context
    })


@login_required
def create_project(request):
    if request.method == "POST":
        title = request.POST.get('title')
        status = request.POST.get('status')
        team_member_ids = request.POST.getlist('team_members')

        project = Project.objects.create(title=title, status=status)
        project.team_members.set(User.objects.filter(id__in=team_member_ids))

        messages.success(request, "Project created successfully.")
        return redirect('projects')

    return redirect('projects')

@login_required
def update_project_status(request, project_id):
    project = Project.objects.get(id=project_id)
    if request.method == "POST":
        status = request.POST.get('status')
        project.status = status
        project.save()
        messages.success(request, "Project status updated.")
    return redirect('projects')

@login_required
def delete_project(request, project_id):
    project = Project.objects.get(id=project_id)
    project.delete()
    messages.success(request, "Project deleted successfully.")
    return redirect('projects')

@login_required
def tasks(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)  # Ensure profile exists
    return render(request, 'app/tasks.html', {'profile': profile})  # Pass profile to template


@login_required
def canvas(request):
    return render(request, 'app/canvas.html')

def get_users(request):
    users = User.objects.values("id", "username")
    return JsonResponse(list(users), safe=False)

# Excalidraw Whiteboard View
@login_required
def excalidraw_whiteboard(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Ensure only project members can access
    if request.user not in project.team_members.all():
        messages.error(request, "You do not have permission to access this whiteboard.")
        return redirect('projects')

    return render(request, 'app/excalidraw.html', {'project': project})

@csrf_exempt
def save_excalidraw_data(request, project_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            project = Project.objects.get(id=project_id)

            whiteboard, created = Whiteboard.objects.get_or_create(project=project)
            whiteboard.drawing_data = data.get("drawing_data", {})
            whiteboard.save()

            return JsonResponse({"status": "success", "message": "Whiteboard saved."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

def get_excalidraw_data(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
        whiteboard = Whiteboard.objects.filter(project=project).first()

        return JsonResponse({
            "status": "success",
            "drawing_data": whiteboard.drawing_data if whiteboard else {}
        })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

def report(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'app/report.html',{'profile': profile})