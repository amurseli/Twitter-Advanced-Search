#!/bin/sh
set -e

echo "Starting X-Scraper Backend..."

# Esperar a que la base de datos esté lista
echo "Waiting for database..."
python << END
import sys
import time
import psycopg2
import os

for i in range(30):
    try:
        conn = psycopg2.connect(
            dbname=os.environ.get('DB_NAME'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            host=os.environ.get('DB_HOST'),
            port=os.environ.get('DB_PORT', '5432')
        )
        conn.close()
        print("Database is ready!")
        break
    except psycopg2.OperationalError:
        print(f"Database not ready, waiting... ({i+1}/30)")
        time.sleep(2)
else:
    print("Database connection failed!")
    sys.exit(1)
END

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Crear superuser si no existe
echo "Checking for superuser..."
python << END
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@xcraper.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

if username and email and password:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser {username} created.")
    else:
        print(f"Superuser {username} already exists.")
else:
    print("Superuser creation skipped - missing credentials.")
END

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-6060} \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -