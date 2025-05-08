from django.db import models


class Conversation(models.Model):
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        CLOSED = 'CLOSED', 'Closed'

    id = models.UUIDField(primary_key=True)
    status = models.CharField(max_length=6, choices=Status.choices, default=Status.OPEN)
    opened_at = models.DateTimeField()
    closed_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Message(models.Model):
    class Direction(models.TextChoices):
        SENT = 'SENT', 'Sent'
        RECEIVED = 'RECEIVED', 'Received'

    id = models.UUIDField(primary_key=True)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages'
    )
    direction = models.CharField(max_length=8, choices=Direction.choices)
    content = models.TextField()
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
