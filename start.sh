#!/bin/bash
set -e
python manage.py migrate --noinput
gunicorn config.wsgi --bind 0.0.0.0:$PORT --timeout 120
