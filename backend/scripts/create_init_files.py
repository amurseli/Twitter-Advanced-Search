"""
Script to create the initial app structure with empty __init__.py files
"""
import os
from pathlib import Path

# Define the app structure
app_structure = {
    'apps': {
        '__init__.py': '',
        'accounts': {
            '__init__.py': '',
            'models.py': 'from django.db import models\n\n# Create your models here.\n',
            'views.py': 'from django.shortcuts import render\n\n# Create your views here.\n',
            'urls.py': 'from django.urls import path\n\nurlpatterns = [\n    # Add URL patterns here\n]\n',
            'serializers.py': 'from rest_framework import serializers\n\n# Create your serializers here.\n',
            'admin.py': 'from django.contrib import admin\n\n# Register your models here.\n',
            'apps.py': '''from django.apps import AppConfig\n\n\nclass AccountsConfig(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = 'apps.accounts'\n''',
            'migrations': {
                '__init__.py': '',
            },
        },
        'scraping': {
            '__init__.py': '',
            'models.py': 'from django.db import models\n\n# Create your models here.\n',
            'views.py': 'from django.shortcuts import render\n\n# Create your views here.\n',
            'urls.py': 'from django.urls import path\n\nurlpatterns = [\n    # Add URL patterns here\n]\n',
            'serializers.py': 'from rest_framework import serializers\n\n# Create your serializers here.\n',
            'admin.py': 'from django.contrib import admin\n\n# Register your models here.\n',
            'apps.py': '''from django.apps import AppConfig\n\n\nclass ScrapingConfig(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = 'apps.scraping'\n''',
            'tasks.py': '''from celery import shared_task\n\n\n@shared_task\ndef example_task():\n    """Example Celery task"""\n    return "Task completed!"\n''',
            'migrations': {
                '__init__.py': '',
            },
        },
        'api': {
            '__init__.py': '',
            'urls.py': '''from django.urls import path, include\n\nurlpatterns = [\n    path('scraping/', include('apps.scraping.urls')),\n    # Add more API endpoints here\n]\n''',
            'views.py': 'from rest_framework.views import APIView\n\n# Create your API views here.\n',
            'apps.py': '''from django.apps import AppConfig\n\n\nclass ApiConfig(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = 'apps.api'\n''',
        },
    },
    'config': {
        '__init__.py': '',
        'settings': {
            '__init__.py': '',
        },
        'wsgi.py': '''"""
WSGI config for X Advanced Search project.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_wsgi_application()
''',
        'asgi.py': '''"""
ASGI config for X Advanced Search project.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_asgi_application()
''',
        'celery.py': '''"""
Celery configuration for X Advanced Search
"""
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('x_advanced_search')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
''',
    },
}


def create_structure(base_path, structure):
    """Recursively create directories and files"""
    for name, content in structure.items():
        path = base_path / name
        
        if isinstance(content, dict):
            # It's a directory
            path.mkdir(exist_ok=True)
            create_structure(path, content)
        else:
            # It's a file
            if not path.exists():
                path.write_text(content)
                print(f"Created: {path}")


if __name__ == "__main__":
    # Get the backend directory
    backend_dir = Path(__file__).parent.parent
    
    # Create the structure
    create_structure(backend_dir, app_structure)
    
    print("\nApp structure created successfully!")