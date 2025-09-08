#!/bin/bash
set -e

echo "Starting Django app..."

if [ ! -z "$DB_HOST" ] && [ ! -z "$DB_PASSWORD" ]; then
    echo "Database configured, running migrations..."
    python manage.py migrate --noinput || echo "Migrations failed, continuing anyway..."
    python manage.py collectstatic --noinput || echo "Collectstatic failed, continuing..."
else
    echo "No database configured, skipping migrations..."
fi

echo "Starting Gunicorn..."
exec "$@"
