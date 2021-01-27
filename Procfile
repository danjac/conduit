release: python manage.py migrate
web: gunicorn --workers=1 --max-requests=1000 --max-requests-jitter=50 conduit.config.asgi -k uvicorn.workers.UvicornWorker
worker: celery -A conduit.config.celery_app worker -l INFO
