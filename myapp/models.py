from django.db import models

# Create your models here.

from django.db import models

class WebhookEvent(models.Model):
    event_id = models.CharField(max_length=255, unique=True)
    received_at = models.DateTimeField(auto_now_add=True)
    payload = models.JSONField()

    def __str__(self):
        return self.event_id

