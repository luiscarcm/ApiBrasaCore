#!/bin/bash
python manage.py migrate --noinput
python manage.py seed
exec gunicorn restaurante.wsgi --log-file -
