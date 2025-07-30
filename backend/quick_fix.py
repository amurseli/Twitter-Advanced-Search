import os
import sys
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

import django
django.setup()

from django.conf import settings
settings.CSRF_TRUSTED_ORIGINS = [
    "https://xcraper-backend-86013019965.us-central1.run.app",
    "https://xcraper.chequeabot.com",
]
