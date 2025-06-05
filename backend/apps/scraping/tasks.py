from celery import shared_task


@shared_task
def example_task():
    """Example Celery task"""
    return "Task completed!"
