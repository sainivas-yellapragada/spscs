from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.login, name='index'),  # Index page as login page
    path('logout/', views.logout_view, name='logout'),  # Logout functionality
    path('home/', login_required(views.home), name='home'),  # Protect home page
]
