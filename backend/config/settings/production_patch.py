# Agregar al final de production.py
CSRF_TRUSTED_ORIGINS = [
    'https://xcraper.chequeabot.com',
    'https://xcraper-86013019965.us-central1.run.app',
]

# Temporalmente para debugging
CORS_ALLOWED_ORIGINS = [
    'https://xcraper.chequeabot.com',
    'http://localhost:6070',
]

CORS_ALLOW_ALL_ORIGINS = True  # Temporal para testing
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
