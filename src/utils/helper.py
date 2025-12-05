from datetime import datetime, timezone
import uuid


def generate_id() -> str:
    return uuid.uuid4().hex


def utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
