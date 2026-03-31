# legacyvault/settings/production.py
"""
Production settings
- DEBUG disabled
- PostgreSQL database (configured via environment variables)
- S3 for static/media storage (optional)
- Stricter security defaults
"""

from .base import *  # noqa: F401,F403
import os

DEBUG = False

# WhiteNoise for static files
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

# Security
SECRET_KEY = os.environ["SECRET_KEY"]  # require in production
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
if not ALLOWED_HOSTS or ALLOWED_HOSTS == [""]:
    raise RuntimeError("ALLOWED_HOSTS must be set in production")

# Database: PostgreSQL (expects env vars)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "legacyvault"),
        "USER": os.environ.get("POSTGRES_USER", "legacyvault"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

# Optional: use DATABASE_URL if provided (common in 12-factor deployments)
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    # Minimal parsing to avoid extra dependencies; if you prefer, use dj-database-url
    import urllib.parse as _up

    _parsed = _up.urlparse(DATABASE_URL)
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": _parsed.path.lstrip("/"),
        "USER": _parsed.username,
        "PASSWORD": _parsed.password,
        "HOST": _parsed.hostname,
        "PORT": _parsed.port or "5432",
    }

# Logging: more conservative in production
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOGGING["root"]["level"] = LOG_LEVEL

# Static and media: optional S3 configuration
USE_S3 = os.environ.get("USE_S3", "false").lower() == "true"
if USE_S3:
    AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

    # Example Django-storages settings (only if you install django-storages)
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_S3_BUCKET_NAME}.s3.amazonaws.com"
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
else:
    # Fallback to filesystem
    STATIC_URL = os.environ.get("STATIC_URL", "/static/")
    MEDIA_URL = os.environ.get("MEDIA_URL", "/media/")
    STORAGES = {
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

# Email: require production-ready backend via env
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "true").lower() == "true"

# Additional production hardening (examples)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "true").lower() == "true"