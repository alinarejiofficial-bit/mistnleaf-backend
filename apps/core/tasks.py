from celery import shared_task


@shared_task
def debug_task():
    return "Celery is configured for Mistnleaf Resort Management System."
