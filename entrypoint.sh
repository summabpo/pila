#!/bin/sh
set -e

export DJANGO_SETTINGS_MODULE=pila_service.settings

echo 'Applying migrations...'
python manage.py migrate --noinput

echo 'Running PILA microservice...'
exec gunicorn --bind 0.0.0.0:8001 pila_service.wsgi:application \
    --workers 2 \
    --timeout 120 \
    --log-level info
