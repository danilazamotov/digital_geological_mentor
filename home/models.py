from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_file = models.BooleanField(default=False)
    audio_file = models.FileField(upload_to='audio/', null=True, blank=True)


class File(models.Model):
    message = models.OneToOneField(Message, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')