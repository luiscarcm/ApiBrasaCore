#!/bin/bash
python manage.py migrate --noinput
exec gunicorn restaurante.wsgi --log-file -
