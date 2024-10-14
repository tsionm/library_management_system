from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import LibraryUser

@receiver(post_save, sender=User)
def create_library_user(sender, instance, created, **kwargs):
    if created:  # Check if the user was just created
        LibraryUser.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_library_user(sender, instance, **kwargs):
    instance.libraryuser.save()  # This ensures that the library user is saved when the user is saved
