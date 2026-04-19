import os


def get_logging_config(environment="development"):
    level = os.environ.get("DJANGO_LOG_LEVEL", "DEBUG" if environment == "development" else "INFO")
    db_level = os.environ.get("DJANGO_DB_LOG_LEVEL", "INFO")
    autoreload_level = os.environ.get("DJANGO_AUTORELOAD_LOG_LEVEL", "INFO")

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(levelname)s %(asctime)s %(name)s %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "level": level,
                "propagate": False,
            },
            "django.db.backends": {
                "handlers": ["console"],
                "level": db_level,
                "propagate": False,
            },
            "django.utils.autoreload": {
                "handlers": ["console"],
                "level": autoreload_level,
                "propagate": False,
            },
        },
    }
