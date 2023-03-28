web: gunicorn app:app --log-file -
worker: celery worker -A app.celery -l INFO