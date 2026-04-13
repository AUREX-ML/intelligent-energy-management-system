from app.tasks.celery_app import celery_app


@celery_app.task(name="tasks.send_alert_notification")
def send_alert_notification(alert_id: str):
    """Send email / push notification when a new alert is triggered."""
    # TODO: implement notification dispatch
    pass
