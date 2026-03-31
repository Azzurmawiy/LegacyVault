"""
Shared configuration used by all environments.
Keep secrets and environment-specific values out of this file.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Basic app settings
APP_NAME = "legacyvault"
DEBUG = False

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core.apps.CoreConfig',
    'accounts.apps.AccountsConfig',
    'django_cleanup.apps.CleanupConfig',
    'axes',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'django_q',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'legacyvault.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'legacyvault.wsgi.application'

# Timezone and localization
TIME_ZONE = os.environ.get("TIME_ZONE", "UTC")
LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "en-us")

# Security defaults (override in production via env vars)
SECRET_KEY = os.environ.get("SECRET_KEY", "replace-me-with-env-secret")

# Allowed hosts default (override in production)
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Logging (simple default; extend per environment)
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": LOG_LEVEL, "handlers": ["console"]},
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "formatters": {
        "default": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"},
    },
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
}

# Static and media defaults
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
STATIC_ROOT = os.environ.get("STATIC_ROOT", str(BASE_DIR / "staticfiles"))
MEDIA_ROOT = os.environ.get("MEDIA_ROOT", str(BASE_DIR / "media"))

STATICFILES_DIRS = [BASE_DIR / 'static']

# Email defaults (use env to override)
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "smtp")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 25))

# Database placeholder (each env should override DATABASES)
DATABASES = {
    "default": {
        "ENGINE": "sqlite3",
        "NAME": str(BASE_DIR / "db.sqlite3"),
    }
}

LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'account_login'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
SITE_ID = 1
ACCOUNT_EMAIL_VERIFICATION = 'none'

# Axes Settings
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1

# Django-Q2 Settings
Q_CLUSTER = {
    'name': 'LegacyVaultQueue',
    'workers': 4,
    'recycle': 500,
    'timeout': 60,
    'compress': True,
    'cpu_affinity': 1,
    'save_limit': 250,
    'queue_limit': 500,
    'label': 'Django Q',
    'orm': 'default'
}

# Third-party integrations placeholders
AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME", "")
AWS_REGION = os.environ.get("AWS_REGION", "")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")

# Feature flags and defaults
FEATURE_FLAGS = {
    "ENABLE_SOME_FEATURE": os.environ.get("ENABLE_SOME_FEATURE", "false").lower() == "true"
}