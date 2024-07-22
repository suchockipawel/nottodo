from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class NotToDo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    context = models.CharField(max_length=50, choices=[('Home', 'Home'), ('Work', 'Work'), ('Other', 'Other')])
    scheduled_start_time = models.DateTimeField(blank=True, null=True)
    scheduled_end_time = models.DateTimeField(blank=True, null=True)
    repeat = models.CharField(max_length=50, choices=[('None', 'None'), ('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly')], default='None')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.repeat not in ['Daily', 'Weekly', 'Monthly', 'None']:
            raise ValidationError('Invalid value for repeat. Must be "None", "Daily", "Weekly", or "Monthly".')

    def __str__(self):
        return self.title

class SharedNotToDo(models.Model):
    nottodo = models.ForeignKey(NotToDo, on_delete=models.CASCADE, related_name='shared_nottodos')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

class Comment(models.Model):
    shared_nottodo = models.ForeignKey(SharedNotToDo, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

class EmailLog(models.Model):
    nottodo = models.ForeignKey(NotToDo, on_delete=models.CASCADE, related_name='email_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Email to {self.email} for {self.nottodo.title}"
