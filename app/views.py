from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from allauth.account.signals import user_signed_up, user_logged_in
from django.dispatch import receiver
from .models import Profile, Project, Whiteboard, Task, ProjectStatusLog, Notification
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from datetime import date, timedelta
from xhtml2pdf import pisa
from django.template.loader import render_to_string
import random
import string
import re

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
    all_projects = Project.objects.all()
    tasks = Task.objects.filter(assigned_to=request.user)
    today = date.today()

    # Categorize tasks
    urgent_tasks = tasks.filter(end_date__lte=today, status__in=['DOING', 'UNFINISHED'])
    minor_tasks = tasks.filter(end_date__gt=today, status__in=['DOING', 'UNFINISHED'])
    pending_tasks = tasks.filter(status='ON_HOLD')

    # Team members and their projects
    team_members_dict = {}
    for task in tasks:
        for user in task.assigned_to.all():
            if user not in team_members_dict:
                team_members_dict[user] = set()
            team_members_dict[user].add(task.project.title)

    # Project stages for chart
    project_stages = {
        "Planning": all_projects.filter(status="Planning").count(),
        "Design": all_projects.filter(status="Design").count(),
        "Building": all_projects.filter(status="In Progress").count(),
        "Testing": all_projects.filter(status="Testing").count()
    }

    login_type = request.session.get('login_type', 'employee')

    # Fetch project-related notifications
    user_projects = Project.objects.filter(team_members=request.user)
    project_status_logs = ProjectStatusLog.objects.filter(project__in=user_projects).order_by('-changed_at')
    project_notifications = [
        {'message': f"Project '{log.project.title}' status changed from {log.old_status} to {log.new_status}", 'date': log.changed_at}
        for log in project_status_logs
    ]

    meeting_notifications = Notification.objects.filter(user=request.user, message__contains="A meeting is scheduled").order_by('-created_at')
    for notification in meeting_notifications:
        # Clean up the message to remove HTML and extract only the link
        message = notification.message
        # Extract the link text between <a href='...' target='_blank'> and </a>
        link_match = re.search(r"<a href='(.*?)' target='_blank'>(.*?)</a>", message)
        if link_match:
            link = link_match.group(2)  # Get the link text (e.g., https://meet.jit.si/sgHYEDIw1z)
            # Remove the HTML part and keep the rest of the message
            cleaned_message = re.sub(r"<a href='.*?' target='_blank'>.*?</a>", link, message)
        else:
            cleaned_message = message  # Fallback if no link is found
        project_notifications.append({'message': cleaned_message, 'date': notification.created_at})

    # Parse meeting notifications for the calendar
    meetings = []
    for notification in meeting_notifications:
        message = notification.message
        try:
            date_str = message.split("on ")[1].split(" at ")[0]
            time_str = message.split("at ")[1].split(" with ")[0]
            link_start = message.index("href='") + 6
            link_end = message.index("'", link_start)
            link = message[link_start:link_end]
            meetings.append({'date': date_str, 'time': time_str, 'link': link})
        except (IndexError, ValueError) as e:
            logger.warning(f"Could not parse meeting notification: {message}, error: {e}")

    # Task deadlines for the calendar
    task_deadlines = [
        {'title': task.title, 'end_date': task.end_date.strftime('%Y-%m-%d')}
        for task in tasks if task.end_date
    ]

    logger.debug(f"Rendering home for {request.user.username}, login_type={login_type}, meetings={meetings}, project_notifications={project_notifications}, task_deadlines={task_deadlines}")
    return render(request, 'app/home.html', {
        'user': request.user,
        'profile': profile,
        'all_projects': all_projects,
        'tasks': tasks,
        'urgent_tasks': urgent_tasks,
        'minor_tasks': minor_tasks,
        'pending_tasks': pending_tasks,
        'team_members_dict': team_members_dict,
        'project_stages': project_stages,
        'login_type': login_type,
        'meetings': meetings,
        'project_notifications': project_notifications,
        'task_deadlines': task_deadlines
    })

@login_required
def admin_home(request):
    if request.session.get('login_type') != 'admin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    
    profile = Profile.objects.filter(user=request.user).first()
    all_projects = Project.objects.all()
    all_users = User.objects.all()
    tasks = Task.objects.all()
    today = date.today()
    
    for task in tasks:
        if task.status not in ['ON_HOLD', 'DONE']:
            if task.end_date < today:
                task.status = 'BACKLOG'
            elif task.start_date <= today <= task.end_date:
                task.status = 'DOING'
            elif task.start_date > today:
                task.status = 'UNFINISHED'
            task.save()

    team_members_dict = {}
    for task in tasks:
        project = task.project
        if project not in team_members_dict:
            team_members_dict[project] = set()
        for user in task.assigned_to.all():
            team_members_dict[project].add(user)

    # Fetch meeting notifications for the current user
    meeting_notifications = Notification.objects.filter(user=request.user, message__contains="A meeting is scheduled")
    meetings = []
    for notification in meeting_notifications:
        message = notification.message
        try:
            date_str = message.split("on ")[1].split(" at ")[0]
            time_str = message.split("at ")[1].split(" with ")[0]
            link_start = message.index("href='") + 6
            link_end = message.index("'", link_start)
            link = message[link_start:link_end]
            meetings.append({'date': date_str, 'time': time_str, 'link': link})
        except (IndexError, ValueError) as e:
            logger.warning(f"Could not parse meeting notification: {message}, error: {e}")

    # Task deadlines for the calendar
    task_deadlines = [
        {'title': task.title, 'end_date': task.end_date.strftime('%Y-%m-%d')}
        for task in tasks if task.end_date
    ]

    login_type = request.session.get('login_type', 'employee')

    logger.debug(f"Rendering admin_home for {request.user.username}, login_type={login_type}, tasks={list(tasks.values('id', 'title', 'status'))}, team_members_dict={[(p.title, [u.username for u in users]) for p, users in team_members_dict.items()]}, meetings={meetings}, task_deadlines={task_deadlines}")
    return render(request, 'app/adminhome.html', {
        'user': request.user,
        'profile': profile,
        'all_projects': all_projects,
        'all_users': all_users,
        'tasks': tasks,
        'team_members_dict': team_members_dict,
        'login_type': login_type,
        'meetings': meetings,
        'task_deadlines': task_deadlines
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
def admin_projects(request):
    if request.session.get('login_type') != 'admin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    
    profile = Profile.objects.get_or_create(user=request.user)[0]
    projects = Project.objects.all()  # Admin sees all projects
    login_type = request.session.get('login_type', 'employee')
    
    return render(request, 'app/admin_projects.html', {
        'profile': profile,
        'projects': projects,
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
        # Redirect based on login_type
        login_type = request.session.get('login_type', 'employee')
        if login_type == 'admin':
            return redirect('admin_projects')
        return redirect('projects')

    # For non-POST requests, redirect based on login_type
    login_type = request.session.get('login_type', 'employee')
    if login_type == 'admin':
        return redirect('admin_projects')
    return redirect('projects')

@login_required
def update_project_status(request, project_id):
    project = Project.objects.get(id=project_id)
    if request.method == "POST":
        old_status = project.status
        new_status = request.POST.get('status')
        if old_status != new_status:
            project.status = new_status
            project.save()
            ProjectStatusLog.objects.create(
                project=project,
                old_status=old_status,
                new_status=new_status
            )
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
    
    if login_type == 'admin':
        return redirect('admin_tasks')

    today = date.today()
    for task in user_tasks:
        if task.status not in ['ON_HOLD', 'DONE']:
            if task.end_date < today:
                task.status = 'BACKLOG'
            elif task.start_date <= today <= task.end_date:
                task.status = 'DOING'
            elif task.start_date > today:
                task.status = 'UNFINISHED'
            task.save()

    logger.debug(f"Tasks for user {request.user.username}: {list(user_tasks.values('id', 'title', 'status'))}")
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
    
    profile = Profile.objects.get_or_create(user=request.user)[0]
    tasks = Task.objects.all()
    all_projects = Project.objects.all()
    all_users = User.objects.all()
    login_type = request.session.get('login_type', 'employee')
    
    today = date.today()
    for task in tasks:
        if task.status not in ['ON_HOLD', 'DONE']:
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
        assigned_to_ids = request.POST.getlist('team_members')
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
        if status in ['ON_HOLD', 'UNFINISHED']:
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
    query = request.GET.get('q', '')  # Use 'q' to match the JavaScript
    if query:
        users = User.objects.filter(username__icontains=query).values("id", "username")[:5]
    else:
        users = []
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
    profile = Profile.objects.get_or_create(user=request.user)[0]
    login_type = request.session.get('login_type', 'employee')

    user_projects = Project.objects.filter(team_members=request.user)
    total_projects = user_projects.count()
    completed_projects = user_projects.filter(status='Completed').count()
    
    user_tasks = Task.objects.filter(assigned_to=request.user)
    total_tasks = user_tasks.count()
    closed_tasks = user_tasks.filter(status='DONE').count()

    projects_progress = (total_projects / 100) * 100
    projects_offset = 377 - (377 * (projects_progress / 100))

    tasks_progress = (closed_tasks / 100) * 100
    tasks_offset = 377 - (377 * (tasks_progress / 100))

    project_summaries = []
    progress_map = {
        'Planning': 25,
        'In Progress': 75,
        'Completed': 100
    }
    for project in user_projects:
        progress = progress_map.get(project.status, 0)
        manager = request.user if login_type == 'admin' else None
        project_summaries.append({
            'name': project.title,
            'manager': f"{manager.first_name} {manager.last_name}" if manager else "N/A",
            'due_date': project.updated_at.strftime('%Y-%m-%d'),
            'status': project.status,
            'progress': progress
        })

    if request.method == "POST" and 'download_pdf' in request.POST:
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
        'projects': project_summaries,
    })

@login_required
def admin_report(request):
    # Ensure only admins can access this view (optional check)
    login_type = request.session.get('login_type', 'employee')
    if login_type != 'admin':
        return HttpResponse("Unauthorized access", status=403)

    # Get the profile for the logged-in user
    profile = Profile.objects.get_or_create(user=request.user)[0]

    # Get ALL projects and tasks (not limited to the current user)
    all_projects = Project.objects.all()
    total_projects = all_projects.count()
    completed_projects = all_projects.filter(status='Completed').count()

    all_tasks = Task.objects.all()
    total_tasks = all_tasks.count()
    closed_tasks = all_tasks.filter(status='DONE').count()

    # Calculate progress for the circular charts
    projects_progress = (total_projects / 100) * 100 if total_projects > 0 else 0
    projects_offset = 377 - (377 * (projects_progress / 100))

    tasks_progress = (closed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
    tasks_offset = 377 - (377 * (tasks_progress / 100))

    # Prepare project summaries for all projects
    project_summaries = []
    progress_map = {
        'Planning': 25,
        'In Progress': 75,
        'Completed': 100
    }
    for project in all_projects:
        progress = progress_map.get(project.status, 0)
        # Assuming project has a manager field; adjust if necessary
        manager = project.manager if hasattr(project, 'manager') else None
        project_summaries.append({
            'name': project.title,
            'manager': f"{manager.first_name} {manager.last_name}" if manager else "N/A",
            'due_date': project.updated_at.strftime('%Y-%m-%d'),
            'status': project.status,
            'progress': progress
        })

    # Handle PDF download
    if request.method == "POST" and 'download_pdf' in request.POST:
        pdf_template = 'app/admin_report_pdf.html'  # Adjust if you have a separate PDF template
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
        response['Content-Disposition'] = 'attachment; filename="admin_report.pdf"'
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('PDF generation failed', status=500)
        return response

    # Render the admin report page
    return render(request, 'app/admin_report.html', {
        'profile': profile,
        'login_type': login_type,
        'total_projects': total_projects,
        'completed_projects': completed_projects,
        'closed_tasks': closed_tasks,
        'total_tasks': total_tasks,
        'projects_offset': projects_offset,
        'tasks_offset': tasks_offset,
        'projects': project_summaries,
    })

@login_required
def notifications(request):
    profile = Profile.objects.get_or_create(user=request.user)[0]
    login_type = request.session.get('login_type', 'employee')
    today = date.today()

    # Task deadline notifications
    user_tasks = Task.objects.filter(assigned_to=request.user)
    deadline_notifications = []
    for task in user_tasks:
        if task.status != 'DONE':
            days_until_deadline = (task.end_date - today).days
            if 0 <= days_until_deadline <= 2:
                deadline_notifications.append({
                    'task_title': task.title,
                    'days_left': days_until_deadline,
                    'end_date': task.end_date
                })

    # Project status change notifications
    user_projects = Project.objects.filter(team_members=request.user)
    project_notifications = []
    recent_logs = ProjectStatusLog.objects.filter(
        project__in=user_projects,
        changed_at__gte=today - timedelta(days=7)
    )
    for log in recent_logs:
        project_notifications.append({
            'project_title': log.project.title,
            'old_status': log.old_status,
            'new_status': log.new_status,
            'updated_at': log.changed_at
        })

    # Meeting notifications from Notification model
    meeting_notifications = Notification.objects.filter(user=request.user, read=False).order_by('-created_at')

    # Combine all notifications into a single list
    notifications_list = []

    # Add task deadline notifications
    for dn in deadline_notifications:
        if dn['days_left'] == 0:
            message = f"Task '{dn['task_title']}' deadline is today!"
        else:
            message = f"Task '{dn['task_title']}' deadline in {dn['days_left']} day{'s' if dn['days_left'] > 1 else ''}!"
        notifications_list.append({'message': message, 'date': dn['end_date']})

    # Add project status change notifications
    for pn in project_notifications:
        message = f"Project '{pn['project_title']}' moved from {pn['old_status']} to {pn['new_status']}."
        notifications_list.append({'message': message, 'date': pn['updated_at']})

    # Add meeting notifications
    for notification in meeting_notifications:
        notifications_list.append({'message': notification.message, 'date': notification.created_at})

    return render(request, 'app/notifications.html', {
        'profile': profile,
        'login_type': login_type,
        'notifications': notifications_list,
    })

@login_required
def admin_notifications(request):
    if request.session.get('login_type') != 'admin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')

    profile = Profile.objects.get_or_create(user=request.user)[0]
    login_type = request.session.get('login_type', 'employee')
    today = date.today()

    # Task deadline notifications (all tasks)
    all_tasks = Task.objects.all()
    task_notifications = []
    for task in all_tasks:
        if task.status != 'DONE':
            days_until_deadline = (task.end_date - today).days
            if 0 <= days_until_deadline <= 2:
                task_notifications.append({
                    'task_title': task.title,
                    'days_left': days_until_deadline,
                    'end_date': task.end_date
                })

    # Project status change notifications (all projects) + meeting notifications
    all_projects = Project.objects.all()
    project_notifications = []
    recent_logs = ProjectStatusLog.objects.filter(
        project__in=all_projects,
        changed_at__gte=today - timedelta(days=7)
    )
    for log in recent_logs:
        project_notifications.append({
            'project_title': log.project.title,
            'old_status': log.old_status,
            'new_status': log.new_status,
            'updated_at': log.changed_at
        })

    # Add meeting notifications to project notifications for admin
    meeting_notifications = Notification.objects.filter(user=request.user, read=False).order_by('-created_at')
    for notification in meeting_notifications:
        project_notifications.append({
            'message': notification.message,
            'date': notification.created_at
        })

    # Prepare notifications for template
    task_notifications_list = []
    for tn in task_notifications:
        if tn['days_left'] == 0:
            message = f"Task '{tn['task_title']}' deadline is today!"
        else:
            message = f"Task '{tn['task_title']}' deadline in {tn['days_left']} day{'s' if tn['days_left'] > 1 else ''}!"
        task_notifications_list.append({'message': message, 'date': tn['end_date']})

    project_notifications_list = []
    for pn in project_notifications:
        if 'project_title' in pn:
            message = f"Project '{pn['project_title']}' moved from {pn['old_status']} to {pn['new_status']}."
            project_notifications_list.append({'message': message, 'date': pn['updated_at']})
        else:
            project_notifications_list.append({'message': pn['message'], 'date': pn['date']})

    return render(request, 'app/admin_notifications.html', {
        'profile': profile,
        'login_type': login_type,
        'task_notifications': task_notifications_list,
        'project_notifications': project_notifications_list,
    })
    
@login_required
def schedule_meeting(request):
    if request.session.get('login_type') != 'admin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')

    if request.method == "POST":
        meeting_datetime = request.POST.get('meeting_datetime')
        agenda = request.POST.get('agenda')
        users_input = request.POST.get('users', '').strip()

        # Generate unique Jitsi meeting link
        meeting_link = generate_jitsi_link()

        # Format the notification message with clickable link
        meeting_date = meeting_datetime.split('T')[0]
        meeting_time = meeting_datetime.split('T')[1]
        message = f"A meeting is scheduled on {meeting_date} at {meeting_time} with agenda: {agenda}. Meeting link: <a href='{meeting_link}' target='_blank'>{meeting_link}</a>"

        # Determine recipients, including the admin
        admin_user = request.user
        if users_input:
            usernames = [u.strip() for u in users_input.split(',') if u.strip()]
            recipients = User.objects.filter(username__in=usernames)
            if recipients.count() != len(usernames):
                messages.warning(request, "Some usernames were not found.")
            if admin_user not in recipients:
                recipients = list(recipients) + [admin_user]
        else:
            recipients = list(User.objects.all())
            if admin_user not in recipients:
                recipients.append(admin_user)

        # Save notifications to the database
        for user in recipients:
            Notification.objects.create(user=user, message=message)
            logger.debug(f"Notification saved for {user.username}: {message}")

        messages.success(request, "Meeting scheduled and notifications sent!")
        return redirect('admin_notifications')

    return redirect('admin_notifications')
# Function to generate unique Jitsi meeting link (moved to bottom)
def generate_jitsi_link():
    room_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return f"https://meet.jit.si/{room_name}"