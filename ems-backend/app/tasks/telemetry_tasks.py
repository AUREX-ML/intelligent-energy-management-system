from app.tasks.celery_app import celery_app


@celery_app.task(name="tasks.aggregate_telemetry")
def aggregate_telemetry(device_id: str):
    """Aggregate telemetry readings for a device (e.g. hourly averages)."""
    # TODO: implement aggregation logic
    pass


@celery_app.task(name="tasks.cleanup_old_telemetry")
def cleanup_old_telemetry(days: int = 90):
    """Delete telemetry records older than the specified number of days."""
    # TODO: implement cleanup logic
    pass
