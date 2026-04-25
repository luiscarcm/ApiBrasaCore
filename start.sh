#!/bin/bash
python manage.py migrate --noinput
python manage.py seed --force
exec gunicorn restaurante.wsgi --log-file -
