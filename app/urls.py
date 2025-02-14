from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', login_required(views.home), name='home'),
    path('register/', views.manual_register, name='register'),
    path('login/', views.login_view, name='manual_login'),
    path('profile/', views.profile_page, name='profile_page'),
    path('tasks/', views.tasks, name='tasks'),
    path('projects/', views.projects, name='projects'),
    path('projects/create/', views.create_project, name='create_project'),
    path('projects/<int:project_id>/update/', views.update_project_status, name='update_project_status'),
    path('projects/<int:project_id>/delete/', views.delete_project, name='delete_project'),
]
