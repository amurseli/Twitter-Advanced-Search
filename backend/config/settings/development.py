"""
Development settings
"""
from .base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

# Django Debug Toolbar (opcional)
try:
    import debug_toolbar
    INSTALLED_APPS += ['debug_toolbar']  # noqa
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa
except ImportError:
    pass

# Debug Toolbar Settings
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Development Database - Use SQLite by default
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # noqa
    }
}

# Email Backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Celery - run synchronously in development (si está instalado)
if 'django_celery_beat' in INSTALLED_APPS:  # noqa
    CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_TASK_ALWAYS_EAGER', default=True)  # noqa
    CELERY_TASK_EAGER_PROPAGATES = True

# CORS - Allow all in development
CORS_ALLOW_ALL_ORIGINS = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
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
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}