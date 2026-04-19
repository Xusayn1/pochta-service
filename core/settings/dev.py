from pathlib import Path

from core import config
from core.log_config import get_logging_config
from .base import *

# Development logging
LOGGING = get_logging_config(environment='development')

# Show SQL queries in console (optional)
LOGGING['loggers']['django.db.backends']['level'] = 'DEBUG'

DEBUG = True
SECRET_KEY = config.SECRET_KEY
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '*']

# Use SQLite by default for local development so the project can boot and
# migrate cleanly without depending on an external database state.
if config.get_bool("USE_POSTGRES", False):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config.DB_NAME,
            'USER': config.DB_USER,
            'PASSWORD': config.DB_PASSWORD,
            'HOST': config.DB_HOST,
            'PORT': config.DB_PORT,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR.parent / 'db.sqlite3',
        }
    }

# Optional: local-specific logging or debug toolbar
INSTALLED_APPS += [
    # 'debug_toolbar',
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'pochta-xizmati-dev',
    }
}

CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"
