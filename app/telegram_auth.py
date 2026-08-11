import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

from .config import BOT_TOKEN


def validate_init_data(init_data: str, max_age_seconds: int = 86400) -> dict | None:
    """
    Validates Telegram Mini App initData per the official Telegram docs:
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app

    Returns the parsed data (with 'user' decoded into a dict) if the
    signature is valid and not expired, otherwise None.
    """
    try:
        parsed = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError:
        return None

    received_hash = parsed.pop("hash", None)
    if not received_hash:
        return None

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))

    secret_key = hmac.new(
        key=b"WebAppData", msg=BOT_TOKEN.encode(), digestmod=hashlib.sha256
    ).digest()
    computed_hash = hmac.new(
        key=secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return None

    auth_date = int(parsed.get("auth_date", 0))
    if time.time() - auth_date > max_age_seconds:
        return None

    if "user" in parsed:
        parsed["user"] = json.loads(parsed["user"])

    return parsed
