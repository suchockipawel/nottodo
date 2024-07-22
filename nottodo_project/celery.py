from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nottodo_project.settings')

app = Celery('nottodo_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

from celery.schedules import crontab
app.conf.beat_schedule = {
    'send-reminders-every-minute': {
        'task': 'nottodo.tasks.check_and_send_reminders',
        'schedule': crontab(minute='*/5'),  # This is checked everyminute for now 
    },
}
app.autodiscover_tasks()
app.conf.timezone = settings.TIME_ZONE
app.conf.enable_utc = True