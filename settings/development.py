# legacyvault/settings/development.py
"""
Development settings
- DEBUG enabled
- Local SQLite database
- Local static/media handling
- Verbose logging
"""

from .base import *  # noqa: F401,F403
import os
from pathlib import Path

DEBUG = True

# Use a simple, local SQLite DB for development
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DEV_SQLITE_PATH", str(BASE_DIR / "dev.sqlite3")),
    }
}

# Allow local hosts
ALLOWED_HOSTS = os.environ.get("DEV_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Easier logging for development
LOG_LEVEL = os.environ.get("DEV_LOG_LEVEL", "DEBUG")
LOGGING["root"]["level"] = LOG_LEVEL

# Email: console backend by default in development
EMAIL_BACKEND = os.environ.get("DEV_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")

# Static/media served from local filesystem
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

# Development-specific feature flags
FEATURE_FLAGS["ENABLE_SOME_FEATURE"] = True
