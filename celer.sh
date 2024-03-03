source .venv/bin/activate
celery -A config.celery_app worker -B -l info
