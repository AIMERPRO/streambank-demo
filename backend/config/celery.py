import os

from celery import Celery
from celery_prometheus import add_prometheus_option

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("streambank")
add_prometheus_option(app)

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
