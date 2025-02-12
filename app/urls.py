from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.login_view, name='login_view'),  # Correct login page path
    path('logout/', views.logout_view, name='logout'),  # Logout functionality
    path('home/', login_required(views.home), name='home'),  # Protect home page
    path('register/', views.manual_register, name='register'),  # Manual Registration
    path('login/', views.login_view, name='manual_login'),  # Ensure this points to the login view
    path('profile/',views.profile_page, name='profile_page'),  # Profile page 
    path('tasks/',views.tasks,name='tasks'),  # Tasks page
    path('projects/',views.projects,name='projects'),  # Projects page
    path('canvas/',views.canvas,name='canvas'),  # Canvas page
]
