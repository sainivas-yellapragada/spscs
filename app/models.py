from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    google_email = models.EmailField(blank=True, null=True)
    google_name = models.CharField(max_length=150, blank=True, null=True)
    github_email = models.EmailField(blank=True, null=True)
    github_name = models.CharField(max_length=150, blank=True, null=True)
    linkedin_email = models.EmailField(blank=True, null=True)
    linkedin_name = models.CharField(max_length=150, blank=True, null=True)
    linkedin_profile_pic = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

# Signal to create a Profile when a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Signal to save the Profile whenever the User instance is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
