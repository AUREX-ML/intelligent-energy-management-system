from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def paginate(query, skip: int = 0, limit: int = 100):
    return query.offset(skip).limit(limit)
