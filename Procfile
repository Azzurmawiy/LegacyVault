web: gunicorn legacyvault.wsgi --log-file -
release: python manage.py migrate
worker: python manage.py qcluster