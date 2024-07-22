import datetime
from django.utils import timezone
from django.core.mail import send_mail
from .models import NotToDo

def get_reminder_times(nottodo):
    reminder_times = []
    start_time = nottodo.scheduled_start_time - datetime.timedelta(minutes=10)
    end_time = nottodo.scheduled_end_time
    current_time = start_time

    delta = None

    if nottodo.repeat == 'Daily':
        delta = datetime.timedelta(days=1)
    elif nottodo.repeat == 'Weekly':
        delta = datetime.timedelta(weeks=1)
    elif nottodo.repeat == 'Monthly':
        delta = datetime.timedelta(weeks=4)  # 4 weeks isn't necessarily a month, but keep to make it easier

    # Ensure delta is set before using it
    if delta is not None:
        while current_time <= end_time:
            reminder_times.append(current_time)
            current_time += delta
    else:
        print(f"Warning: No valid repeat interval set for NotToDo item '{nottodo.title}'")

    return reminder_times

def send_reminder_email(user, nottodo):
    subject = f"Reminder: {nottodo.title}"
    message = f"This is a reminder for your NotToDo item '{nottodo.title}' starting at {nottodo.scheduled_start_time}."
    send_mail(subject, message, 'dci-team-1@dci.com', [user.email])
