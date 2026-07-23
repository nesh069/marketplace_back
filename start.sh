#!/bin/bash
set -e
python manage.py migrate --noinput
gunicorn config.wsgi --bind 0.0.0.0:${PORT:-8000} --timeout 120
