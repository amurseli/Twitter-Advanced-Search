#!/bin/bash
set -e

echo "Starting X Scraper Backend..."

# Intentar migraciones pero no fallar si hay error
echo "Attempting migrations..."
python manage.py migrate --noinput 2>/dev/null || echo "Migrations skipped (DB might already be migrated)"

# Intentar collectstatic pero no fallar
echo "Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || echo "Collectstatic skipped"

# Crear superuser si no existe (opcional)
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'xcraper2025')" | python manage.py shell 2>/dev/null || echo "Admin user creation skipped"

echo "Starting Gunicorn..."
exec "$@"
