from django.db import models
from django.contrib.auth.models import User
import uuid

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


class Project(models.Model):
    STATUS_CHOICES = [
        ('Planning', 'Planning'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    title = models.CharField(max_length=255)
    team_members = models.ManyToManyField(User)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Planning')
    excalidraw_link = models.URLField(blank=True, null=True)  # Link to Excalidraw whiteboard
    excalidraw_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.excalidraw_link:
            # Generate a unique Excalidraw link if not already set
            self.excalidraw_link = f"https://excalidraw.com/#room={uuid.uuid4()}"
            print(f"Generated Excalidraw link for project {self.title}: {self.excalidraw_link}")  # Debugging line
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
