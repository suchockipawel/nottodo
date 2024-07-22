
from django.core.mail import send_mail
from django.utils import timezone
from .models import NotToDo, EmailLog
from .utils import get_reminder_times
from celery import shared_task

@shared_task
def send_nottodo_notifications():
    now = timezone.now()
    time_threshold = now + timezone.timedelta(minutes=10)
    nottodos = NotToDo.objects.filter(
        scheduled_start_time__lte=time_threshold,
        scheduled_start_time__gte=now
    )
    for nottodo in nottodos:
        subject = 'Not To Do Reminder'
        message = f'Remember not to do: {nottodo.title}'
        email = nottodo.user.email

        send_mail(
            subject,
            message,
            'not.todo.project.app@gmail.com',
            [email],
            fail_silently=False,
        )

        # Log the email
        EmailLog.objects.create(
            nottodo=nottodo,
            user=nottodo.user,
            email=email,
            subject=subject,
            message=message,
            sent_at=timezone.now()
        )

        # Print to console for verification
        print(f"Sent email to {email} for NotToDo: {nottodo.title} at {timezone.now()}")
        print("Email sent successfully!")

@shared_task
def check_and_send_reminders():
    now = timezone.now()
    nottodos = NotToDo.objects.filter(scheduled_start_time__gte=now)

    for nottodo in nottodos:
        reminder_times = get_reminder_times(nottodo)
        for reminder_time in reminder_times:
            if now >= reminder_time and now <= (reminder_time + timezone.timedelta(minutes=10)):
                subject = 'Not To Do Reminder'
                message = f'Remember not to do: {nottodo.title}'
                email = nottodo.user.email

                send_mail(
                    subject,
                    message,
                    'not.todo.project.app@gmail.com',
                    [email],
                    fail_silently=False,
                )

                # Log the email
                EmailLog.objects.create(
                    nottodo=nottodo,
                    user=nottodo.user,
                    email=email,
                    subject=subject,
                    message=message,
                    sent_at=timezone.now()
                )

                # Print to console for verification
                print(f"Sent reminder email to {email} for NotToDo: {nottodo.title} at {timezone.now()}")
                print("Reminder email sent successfully!")
