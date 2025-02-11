from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    language = models.CharField(max_length=50, null=True, blank=True)

    google_email = models.EmailField(null=True, blank=True)
    google_name = models.CharField(max_length=255, null=True, blank=True)
    github_email = models.EmailField(null=True, blank=True)
    github_name = models.CharField(max_length=255, null=True, blank=True)
    facebook_email = models.EmailField(null=True, blank=True)
    facebook_name = models.CharField(max_length=255, null=True, blank=True)

    profile_picture = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.user.username
