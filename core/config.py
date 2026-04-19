import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


def _load_env_file():
    if not ENV_FILE.exists():
        return

    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_env_file()


def get_env(name, default=None):
    return os.environ.get(name, default)


def get_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_list(name, default=None, separator=","):
    value = os.environ.get(name)
    if value is None:
        return default or []
    return [item.strip() for item in value.split(separator) if item.strip()]


DJANGO_SETTINGS_MODULE = get_env("DJANGO_SETTINGS_MODULE", "core.settings.dev")
SECRET_KEY = get_env("SECRET_KEY", "django-insecure-change-me")
DEBUG = get_bool("DEBUG", True)
ALLOWED_HOSTS = get_list("ALLOWED_HOSTS", ["127.0.0.1", "localhost"])

DB_NAME = get_env("DB_NAME", "postgres")
DB_PORT = get_env("DB_PORT", "5432")
DB_HOST = get_env("DB_HOST", "localhost")
DB_USER = get_env("DB_USER", "postgres")
DB_PASSWORD = get_env("DB_PASSWORD", "")
DB_SSLMODE = get_env("DB_SSLMODE", "prefer")

TELEGRAM_CHANNEL_ID = get_env("TELEGRAM_CHANNEL_ID", "")
TELEGRAM_BOT_TOKEN = get_env("TELEGRAM_BOT_TOKEN", "")
