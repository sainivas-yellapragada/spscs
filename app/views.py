from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from allauth.account.signals import user_signed_up, user_logged_in
from django.dispatch import receiver
from .models import Profile, Project, Whiteboard, Task
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from datetime import date
from xhtml2pdf import pisa
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

# Custom login page
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        login_type = request.POST.get('login_type', 'employee')
        
        logger.debug(f"Manual login attempt: username={username}, login_type={login_type}")
        request.session['login_type'] = login_type

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            Profile.objects.get_or_create(user=user)
            logger.debug(f"User {user.username} logged in manually, login_type={login_type}")
            messages.success(request, "Logged in successfully!")
            return redirect('admin_home' if login_type == 'admin' else 'home')
        else:
            messages.error(request, "Invalid credentials. Please try again.")
            logger.debug("Manual login failed: invalid credentials")
            return redirect('login_view')

    login_type = request.GET.get('login_type', request.session.get('login_type', 'employee'))
    request.session['login_type'] = login_type
    logger.debug(f"Login page GET: login_type={login_type}, session={request.session['login_type']}")
    return render(request, 'app/login.html')

# Home page (protected) - Employee landing page
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

    # Get all tasks for the user and update statuses dynamically
    user_tasks = Task.objects.filter(assigned_to=request.user)
    today = date.today()
    for task in user_tasks:
        if task.status not in ['ON_HOLD', 'DONE']:  # Preserve admin/employee-set statuses
            if task.end_date < today:
                task.status = 'BACKLOG'
            elif task.start_date <= today <= task.end_date:
                task.status = 'DOING'
            elif task.start_date > today:
                task.status = 'UNFINISHED'
            task.save()

    # Task urgency categorization
    urgent_tasks = user_tasks.filter(status__in=['DOING', 'BACKLOG'])  # Include all DOING and BACKLOG tasks
    minor_tasks = user_tasks.filter(status='UNFINISHED', start_date__gt=today)  # Future tasks
    pending_tasks = user_tasks.filter(status='ON_HOLD')  # On Hold tasks

    logger.debug(f"User {request.user.username} tasks - Urgent: {list(urgent_tasks.values('id', 'title', 'status', 'start_date', 'end_date'))}, Minor: {list(minor_tasks.values('id', 'title', 'status', 'start_date', 'end_date'))}, Pending: {list(pending_tasks.values('id', 'title', 'status', 'start_date', 'end_date'))}")

    login_type = request.session.get('login_type', 'employee')

    logger.debug(f"Rendering home for {request.user.username}, login_type={login_type}")
    return render(request, 'app/home.html', {
        'user': request.user,
        'profile': profile,
        'team_members_dict': team_members_dict,
        'urgent_tasks': urgent_tasks,
        'minor_tasks': minor_tasks,
        'pending_tasks': pending_tasks,
        'login_type': login_type
    })  

# Admin Home page (protected) - Admin landing page
@login_required
def admin_home(request):
    if request.session.get('login_type') != 'admin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    
    profile = Profile.objects.filter(user=request.user).first()
    all_projects = Project.objects.all()
    all_users = User.objects.all()
    tasks = Task.objects.all()  # Fetch all tasks for admin overview
    today = date.today()
    
    # Update task statuses dynamically
    for task in tasks:
        if task.status not in ['ON_HOLD', 'DONE']:  # Preserve admin/employee-set statuses
            if task.end_date < today:
                task.status = 'BACKLOG'
            elif task.start_date <= today <= task.end_date:
                task.status = 'DOING'
            elif task.start_date > today:
                task.status = 'UNFINISHED'
            task.save()

    # Build team_members_dict with project as "team" and users assigned to its tasks
    team_members_dict = {}
    for task in tasks:
        project = task.project
        if project not in team_members_dict:
            team_members_dict[project] = set()
        for user in task.assigned_to.all():
            team_members_dict[project].add(user)

    login_type = request.session.get('login_type', 'employee')

    logger.debug(f"Rendering admin_home for {request.user.username}, login_type={login_type}, tasks={list(tasks.values('id', 'title', 'status'))}, team_members_dict={[(p.title, [u.username for u in users]) for p, users in team_members_dict.items()]}")
    return render(request, 'app/adminhome.html', {
        'user': request.user,
        'profile': profile,
        'all_projects': all_projects,
        'all_users': all_users,
        'tasks': tasks,
        'team_members_dict': team_members_dict,
        'login_type': login_type
    })

# Logout user
def logout_view(request):
    logger.debug(f"Logging out user {request.user.username}")
    logout(request)
    request.session.pop('login_type', None)
    return redirect('login_view')

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

    login_type = request.session.get('login_type', 'employee')
    logger.debug(f"Social signup for {user.username}, login_type={login_type}")

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

# Custom redirect handler for social logins
def social_login_redirect(request):
    if request.user.is_authenticated:
        login_type = request.session.get('login_type', 'employee')
        logger.debug(f"Social login redirect: {request.user.username}, login_type={login_type}")
        return redirect('admin_home' if login_type == 'admin' else 'home')
    logger.debug("Social login redirect: User not authenticated")
    return redirect('login_view')

@login_required
def profile_page(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)
    login_type = request.session.get('login_type', 'employee')

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
        'login_type': login_type
    })

@login_required
def projects(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    user_projects = Project.objects.filter(team_members=request.user)
    users = User.objects.all()
    login_type = request.session.get('login_type', 'employee')
    
    return render(request, 'app/projects.html', {
        'projects': user_projects, 
        'users': users,
        'profile': profile,
        'login_type': login_type
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
    profile, _ = Profile.objects.get_or_create(user=request.user)
    user_tasks = Task.objects.filter(assigned_to=request.user)
    login_type = request.session.get('login_type', 'employee')
    
    # Redirect admins to admin_tasks
    if login_type == 'admin':
        return redirect('admin_tasks')

    # Log the tasks for debugging
    logger.debug(f"Tasks for user {request.user.username}: {list(user_tasks.values('id', 'title', 'status'))}")

    # Update task statuses dynamically for employees
    today = date.today()
    for task in user_tasks:
        if task.status not in ['ON_HOLD', 'DONE']:  # Admin-controlled or employee-set statuses
            if task.end_date < today:
                task.status = 'BACKLOG'
            elif task.start_date <= today <= task.end_date:
                task.status = 'DOING'
            elif task.start_date > today:
                task.status = 'UNFINISHED'
            task.save()

    return render(request, 'app/tasks.html', {
        'profile': profile,
        'tasks': user_tasks,
        'login_type': login_type
    })

@login_required
def mark_task_complete(request, task_id):
    if request.method == "POST":
        task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
        task.status = 'DONE'
        task.save()
        messages.success(request, "Task marked as complete!")
    return redirect('tasks')

@login_required
def admin_tasks(request):
    if request.session.get('login_type') != 'admin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    
    profile, _ = Profile.objects.get_or_create(user=request.user)
    tasks = Task.objects.all()
    all_projects = Project.objects.all()
    all_users = User.objects.all()
    login_type = request.session.get('login_type', 'employee')
    
    # Update task statuses dynamically, preserving ON_HOLD and DONE
    today = date.today()
    for task in tasks:
        if task.status not in ['ON_HOLD', 'DONE']:  # Admin-controlled or employee-set
            if task.end_date < today:
                task.status = 'BACKLOG'
            elif task.start_date <= today <= task.end_date:
                task.status = 'DOING'
            elif task.start_date > today:
                task.status = 'UNFINISHED'
            task.save()

    return render(request, 'app/admintasks.html', {
        'profile': profile,
        'tasks': tasks,
        'all_projects': all_projects,
        'all_users': all_users,
        'login_type': login_type
    })

@login_required
def create_task(request):
    if request.session.get('login_type') != 'admin':
        return redirect('home')
    
    if request.method == "POST":
        title = request.POST.get('title')
        project_id = request.POST.get('project')
        assigned_to_ids = request.POST.getlist('team_members')  # From JS hidden inputs
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        status = request.POST.get('status', 'UNFINISHED')

        logger.debug(f"Creating task: title={title}, project_id={project_id}, assigned_to_ids={assigned_to_ids}, start_date={start_date}, end_date={end_date}, status={status}")

        project = Project.objects.get(id=project_id)
        task = Task.objects.create(
            title=title,
            project=project,
            start_date=start_date,
            end_date=end_date,
            status=status if status in ['ON_HOLD', 'UNFINISHED'] else 'UNFINISHED'
        )
        if assigned_to_ids:
            task.assigned_to.set(User.objects.filter(id__in=assigned_to_ids))
            logger.debug(f"Task assigned to users: {task.assigned_to.all()}")
        else:
            logger.warning("No users assigned to the task!")
        
        messages.success(request, "Task created successfully.")
        return redirect('admin_tasks')
    
    return redirect('admin_tasks')

@login_required
def update_task_status(request, task_id):
    if request.session.get('login_type') != 'admin':
        return redirect('home')
    
    task = get_object_or_404(Task, id=task_id)
    if request.method == "POST":
        status = request.POST.get('status')
        if status in ['ON_HOLD', 'UNFINISHED']:  # Only admin can set these
            task.status = status
            task.save()
            messages.success(request, "Task status updated.")
    return redirect('admin_tasks')

@login_required
def delete_task(request, task_id):
    if request.session.get('login_type') != 'admin':
        return redirect('home')
    
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    messages.success(request, "Task deleted successfully.")
    return redirect('admin_tasks')

@login_required
def canvas(request):
    login_type = request.session.get('login_type', 'employee')
    return render(request, 'app/canvas.html', {'login_type': login_type})

def get_users(request):
    users = User.objects.values("id", "username")
    return JsonResponse(list(users), safe=False)

@login_required
def excalidraw_whiteboard(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    login_type = request.session.get('login_type', 'employee')

    if request.user not in project.team_members.all():
        messages.error(request, "You do not have permission to access this whiteboard.")
        return redirect('projects')

    return render(request, 'app/excalidraw.html', {
        'project': project,
        'login_type': login_type
    })

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

@login_required
def report(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    login_type = request.session.get('login_type', 'employee')

    # Total Projects and Projects in Testing (final stage)
    user_projects = Project.objects.filter(team_members=request.user)
    total_projects = user_projects.count()
    completed_projects = user_projects.filter(status='Testing').count()  # Final stage is Testing
    
    # Closed Tasks
    user_tasks = Task.objects.filter(assigned_to=request.user)
    total_tasks = user_tasks.count()
    closed_tasks = user_tasks.filter(status='DONE').count()

    # Calculate offsets for donut charts (circumference = 2πr = 377 for r=60)
    # Projects: Percentage of total projects out of a fixed maximum of 100
    projects_progress = (total_projects / 100) * 100  # Scale to 100 as max
    projects_offset = 377 - (377 * (projects_progress / 100))

    # Tasks: Percentage of closed tasks out of a fixed maximum of 100
    tasks_progress = (closed_tasks / 100) * 100  # Scale to 100 as max
    tasks_offset = 377 - (377 * (tasks_progress / 100))

    #logger.debug(f"Report data - total_projects: {total_projects}, completed_projects: {completed_projects}, total_tasks: {total_tasks}, closed_tasks: {closed_tasks}, projects_offset: {projects_offset}, tasks_offset: {tasks_offset}")

    # Project summary data
    project_summaries = []
    progress_map = {
        'Planning': 25,
        'In Progress': 75,
        'Testing': 100  # Final stage is Testing
    }
    for project in user_projects:
        progress = progress_map.get(project.status, 0)  # Default to 0 if status not in map
        manager = request.user if login_type == 'admin' else None  # Admin is the manager
        project_summaries.append({
            'name': project.title,
            'manager': f"{manager.first_name} {manager.last_name}" if manager else "N/A",
            'due_date': project.updated_at.strftime('%Y-%m-%d'),  # Using updated_at as due_date isn't present
            'status': project.status,
            'progress': progress
        })

    if request.method == "POST" and 'download_pdf' in request.POST:
        # Generate PDF
        pdf_template = 'app/report_pdf.html'
        context = {
            'user': request.user,
            'total_projects': total_projects,
            'completed_projects': completed_projects,
            'closed_tasks': closed_tasks,
            'total_tasks': total_tasks,
            'projects': project_summaries,
            'login_type': login_type,
        }
        html = render_to_string(pdf_template, context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('PDF generation failed', status=500)
        return response

    return render(request, 'app/report.html', {
        'profile': profile,
        'login_type': login_type,
        'total_projects': total_projects,
        'completed_projects': completed_projects,
        'closed_tasks': closed_tasks,
        'total_tasks': total_tasks,
        'projects_offset': projects_offset,
        'tasks_offset': tasks_offset,
        'projects': project_summaries,  # For the table
    })