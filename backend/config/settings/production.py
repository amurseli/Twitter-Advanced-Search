"""
Production settings for Cloud Run
"""
from .base import *
import os

DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[
    '.run.app',
    'xcraper-backend-86013019965.us-central1.run.app',
    'localhost',
    '127.0.0.1',
    '*'
])

# Database - Cloud SQL PostgreSQL
# La instancia es 'cms', la base de datos es 'xcraper'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='xcraper'),
        'USER': env('DB_USER', default='xcraper'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),  # /cloudsql/chequeado-249220:us-central1:cms
        'PORT': env('DB_PORT', default='5432'),
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Security
SECURE_SSL_REDIRECT = False  # Cloud Run maneja HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS
CORS_ALLOWED_ORIGINS = [
    "https://xcraper.chequeabot.com",
    "http://localhost:6070",
    "http://127.0.0.1:6070",
]

# CSRF
CSRF_TRUSTED_ORIGINS = [
    "https://xcraper-backend-86013019965.us-central1.run.app",
    "https://xcraper.chequeabot.com",
]

# Logging para Cloud Run
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Desactivar Celery en producción por ahora
CELERY_TASK_ALWAYS_EAGER = True