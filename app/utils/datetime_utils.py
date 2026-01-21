from datetime import datetime
from app.constants.config import Config

def format_iso_datetime(value: str):
    return datetime.fromisoformat(value).strftime(Config.DATE_FORMAT)
    