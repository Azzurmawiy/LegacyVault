web: gunicorn legacyvault.wsgi --log-file -
release: python manage.py migrate && python manage.py collectstatic --noinput
worker: python manage.py qcluster