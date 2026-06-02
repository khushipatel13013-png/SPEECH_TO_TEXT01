# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class SpeechHistory(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    audio_file = models.FileField(
    upload_to='audio/',
    null=True,
    blank=True
)

    original_text = models.TextField()

    corrected_text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)